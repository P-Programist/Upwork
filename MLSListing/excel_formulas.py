import datetime as dt
from math import ceil
from scipy import optimize
import numpy_financial as np
import price_relations as pr
from loggers import error_logger as elgr


class Formulas(object):
    def __init__(self, data) -> None:
        self.data = data
        self.rooms = self.data.get("rooms")
        self.TOTALS = {}
        self.O31_Y31 = []
        self.D30_D39 = 15292
        self.J18 = 36

        self.broker = False  # C11
        self.debt_financing = True  # J6
        self.mezzanine_financing = True  # J26

        self.zip_code = self.data.get("zip_code")  # C7
        self.total_rooms = sum([tp[1] for tp in self.rooms])  # C29

        # Sale Assumptions
        self.sale_period = 48  # C15
        self.holding_period = self.sale_period // 12  # C14
        self.selling_costs = 0.04  # C16
        self.annual_appreciations = 0.03  # C17

        # Tax Assumptions
        self.depreciation_life = 27.5  # C21
        self.tax_rate = 0.2  # C22
        self.capital_gain_tax = 0.25  # C23

        # Operating Assumptions: Per Unit
        self.managment_per_unit = 35  # F7
        self.pest_trash_per_unit = 250  # F8
        self.insurance_per_unit = 1000  # F9
        self.water_per_unit = 125  # F10
        self.utilities_per_unit = 10  # F11
        self.maintenance_per_unit = 50  # F12
        self.snow_landscape_per_unit = 50  # F13
        self.vacancy = 0.02  # F16

        # Capex Assumptions
        self.initial_capex = 10000  # F19
        if self.broker:
            self.capex = (-0.9) * (
                0.02 * self.data.get("price")
            ) + self.initial_capex  # O7
        else:
            self.capex = self.initial_capex

        # Operating Assumptions
        self.taxes = self.data.get("taxes")
        self.managment = self.managment_per_unit * self.total_rooms * 12  # G7
        self.pest_trash = self.pest_trash_per_unit * 12  # G8
        self.insurance = self.insurance_per_unit * self.total_rooms  # G9
        self.water = self.water_per_unit * self.total_rooms * 12  # G10
        self.utilities = self.utilities_per_unit * self.total_rooms * 12  # G11
        self.maintenance = self.maintenance_per_unit * self.total_rooms * 12  # G12
        self.snow_landscape = self.snow_landscape_per_unit * 12  # G13

        self.opex_annual = sum(  # G5
            [
                self.taxes,
                self.managment,
                self.pest_trash,
                self.insurance,
                self.water,
                self.utilities,
                self.maintenance,
                self.snow_landscape,
            ]
        )

        self.D29 = self.rent_roll_assumptions()  # D29

        # self.opex_ratio = ceil(self.opex_annual / (self.D29 * 12))  # G14

        # Senior Debt Assumptions
        self.down_payment_percent = 0.25  # J7
        self.down_payment_sum = self.down_payment_percent * self.data.get("price")  # J8

        self.total_investment = int(self.down_payment_sum + self.initial_capex)

        self.assumed_value = np.fv(
            self.annual_appreciations / 12,
            self.sale_period,
            0,
            -self.data.get("price"),
        )

        self.sale_proceeds_cash_flow = self.assumed_value * (1 - self.selling_costs)

        self.loan_amount = self.senior_debt_assumptions().get("loan_amount")
        self.monthly_payment = self.senior_debt_assumptions().get("monthly_payment")
        self.interest_rate = self.senior_debt_assumptions().get("interest_rate")

        refi_table_interest = int(self.loan_amount * (self.interest_rate / 12))
        refi_table_principal = self.monthly_payment - refi_table_interest

        self.REFI_TABLE = {
            1: {
                "beginning_bal": self.loan_amount,
                "refi_table_interest": refi_table_interest,
                "refi_table_principal": refi_table_principal,
                "ending_bal": self.loan_amount - refi_table_principal,
            },
        }

        for j in range(2, 361):
            refi_table_interest_dynamic = round(
                self.REFI_TABLE.get(j - 1).get("ending_bal") * self.interest_rate / 12
            )
            refi_table_principal_dynamic = (
                self.monthly_payment - refi_table_interest_dynamic
            )
            self.REFI_TABLE.update(
                {
                    j: {
                        "beginning_bal": self.REFI_TABLE.get(j - 1).get("ending_bal"),
                        "refi_table_interest": refi_table_interest_dynamic,
                        "refi_table_principal": refi_table_principal_dynamic,
                        "ending_bal": self.REFI_TABLE.get(j - 1).get("ending_bal")
                        - refi_table_principal_dynamic,
                    }
                },
            )

        self.net_proceed = self.sale_proceeds_cash_flow - self.REFI_TABLE.get(  # M24
            self.sale_period
        ).get("ending_bal")

        self.CASH_FLOW_TABLE = {
            1: {
                "gpi": self.D30_D39,
                "vl": self.D30_D39 * self.vacancy,
                "opex": (self.opex_annual / 12),
                "capex": -self.capex / 12,
                "dbtsvrs": -(self.monthly_payment),
            }
        }

        for i in range(2, self.holding_period + 1):
            current_gpi = round(
                self.CASH_FLOW_TABLE[i - 1].get("gpi")
                + (self.CASH_FLOW_TABLE[i - 1].get("gpi") * 0.01),
                0,
            )
            current_opex = round(
                self.CASH_FLOW_TABLE[i - 1].get("opex")
                + (self.CASH_FLOW_TABLE[i - 1].get("opex") * 0.02)
            )

            current_capex = round(self.CASH_FLOW_TABLE[i - 1].get("capex") * 0, 0)

            self.CASH_FLOW_TABLE.update(
                {
                    i: {
                        "gpi": current_gpi,
                        "vl": ceil(current_gpi * self.vacancy),
                        "opex": current_opex,
                        "capex": current_capex,
                        "dbtsvrs": -(self.monthly_payment),
                    },
                }
            )

    def senior_debt_assumptions(self):  # J13
        interest_rate = 0.0375  # J10

        loan_amount = 0
        monthly_payment = 0

        if self.debt_financing:
            loan_amount = (1 - self.down_payment_percent) * self.data.get("price")  # J9
            monthly_payment = round(
                (np.pmt((interest_rate / 12), 360, -loan_amount, 0)), 0
            )
        return {
            "loan_amount": loan_amount,
            "monthly_payment": monthly_payment,
            "interest_rate": interest_rate,
        }

    def mezzanine_debt_assumptions(self):
        loan_amount = self.data.get("price") * 0  # J19
        refinance_term = 300  # J20
        refinance_rate = 0.043  # J21
        monthly_payment = np.pmt(  # J23
            (refinance_rate / 12),
            refinance_term,
            -loan_amount,
            0,
        )

        return monthly_payment

    def rent_roll_assumptions(self):
        total_price = 0
        for pair in self.rooms:
            total_units, unit_amount = pair
            total_price += pr.STATIC_ROOM_PRICE.get(total_units) * unit_amount
        return total_price

    def table(self):
        accumulated_depreciation = 0
        cashflow_list = []

        dates = [
            dt.date(2021, 2, 1),
            dt.date(2022, 2, 1),
            dt.date(2023, 2, 1),
            dt.date(2024, 2, 1),
            dt.date(2025, 1, 31),
            dt.date(2026, 1, 31),
            dt.date(2027, 1, 31),
            dt.date(2028, 1, 31),
            dt.date(2029, 1, 30),
            dt.date(2030, 1, 30),
            dt.date(2031, 1, 30),
            dt.date(2032, 1, 30),
        ]

        table_capex = 10000  # O18

        for i in range(1, self.holding_period + 1):
            rental_income = self.CASH_FLOW_TABLE.get(i).get("gpi") * 12  # O10
            if i == 1:
                table_capex = abs(self.CASH_FLOW_TABLE.get(i).get("capex") * 12)  # O18

            else:
                table_capex = 0

            vacancy_loss = self.CASH_FLOW_TABLE.get(i).get("vl") * 12  # O11

            egi = rental_income - vacancy_loss  # O12

            opex = self.CASH_FLOW_TABLE.get(i).get("opex") * 12  # O14
            noi = egi - opex + i  # O14

            debit_service = abs(
                self.CASH_FLOW_TABLE.get(i).get("dbtsvrs") * 12 - (i - 1)
            )  # O19

            cash_flows_from_operations = noi - table_capex - debit_service + i  # O21

            sale_proceed = 0

            if i == self.holding_period:
                sale_proceed = self.net_proceed

            cash_flow_before_tax = cash_flows_from_operations + sale_proceed  # O25

            depreciation = self.data.get("price") / -self.depreciation_life  # O27
            taxes = ceil(  # O28
                (cash_flows_from_operations + depreciation) * self.tax_rate
            )

            accumulated_depreciation += round(abs(depreciation), 0)  # O29

            capital_gains_tax = 0

            if sale_proceed > 0:
                capital_gains_tax = (  # O30
                    self.assumed_value
                    - self.data.get("price")
                    + accumulated_depreciation
                ) * self.capital_gain_tax

            if taxes < 0:
                cash_flow_after_tax = int(cash_flow_before_tax - capital_gains_tax) + i
            else:
                cash_flow_after_tax = (
                    int(cash_flow_before_tax - taxes - capital_gains_tax) + i
                )

            self.O31_Y31.append(cash_flow_after_tax)
            cashflow_list.append((dates[i], (cash_flow_after_tax)))

            self.TOTALS.update(
                {
                    i: {
                        "rental_income": rental_income,
                        "vacancy_loss": vacancy_loss,
                        "egi": egi,
                        "opex": opex,
                        "noi": noi,
                        "capex": table_capex,
                        "debit_service": debit_service,
                        "cash_flows_from_operations": cash_flows_from_operations,
                        "depreciation": depreciation,
                        "taxes": taxes,
                        "accumulated_depreciation": accumulated_depreciation,
                        "capital_gains_tax": 0,
                        "cash_flow_after_tax": cash_flow_after_tax,
                        "sale_proceeds": 0,
                    },
                }
            )
        self.TOTALS.get(self.holding_period).update(
            {
                "capital_gains_tax": capital_gains_tax,
                "sale_proceeds": self.net_proceed,
            }
        )
        cashflow_list.insert(0, (dates[0], -self.down_payment_sum))

        return round(xirr(cashflow_list) * 1000 / 10, 2)

    def monthly_cash_flow(self):  # J34
        return round(self.D29 - (self.opex_annual / 12) - self.monthly_payment, 0)

    def cash_on_cash(self):
        return round(
            (
                (self.monthly_cash_flow() * 12)
                / (self.down_payment_sum + self.capex)
                * 1000
                / 10
            ),
            1,
        )

    def equity_multiple(self):
        return round(sum(self.O31_Y31) / self.down_payment_sum, 3)

    def __call__(self, *args, **kwds):
        return {
            "IRR": self.table(),
            "CASH_ON_CASH": self.cash_on_cash(),
            "EQUITY_MULTIPLE": self.equity_multiple(),
            "TOTAL_INVESTMENT": self.total_investment,
        }


def xnpv(rate, cashflows):
    return sum(
        [
            cf / (1 + rate) ** ((t - cashflows[0][0]).days / 365.0)
            for (t, cf) in cashflows
        ]
    )


def xirr(cashflows, guess=0.1):
    try:
        return optimize.newton(lambda r: xnpv(r, cashflows), guess)
    except Exception as e:
        elgr().error(e)
        return 0



