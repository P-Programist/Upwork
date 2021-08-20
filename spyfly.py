import json
import requests
from bs4 import BeautifulSoup
from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse


JS_TEMPLATES = {
    "spyfly": '''function autoFill() {
    var first_name = document.getElementById("first-name");
    first_name.value = "%s";

    var last_name = document.getElementById("last-name");
    last_name.value = "%s";

    var city_state = document.getElementById("form-states");
    city_state.value = "%s";

    var search_btn = document.getElementById("search-now").click();
}
autoFill();''',
}




scrapfly_connection: ScrapeApiResponse = ScrapflyClient(
    key='9fbccf4ea11c439c91aec5333852e492',
    max_concurrency=2
)


class SpyFly:
    def __init__(self, user_data_list) -> None:
        self.user_data_list = user_data_list
        self.platform = 'spyfly'


    def do_search(self) -> str:
        user_responses = []

        for user_data in self.user_data_list:
            js_code_template: str = JS_TEMPLATES.get(self.platform) % (
                user_data.get('first_name'), 
                user_data.get('last_name'), 
                user_data.get('state')
            )

            try:
                api_response: ScrapeApiResponse = scrapfly_connection.scrape(
                    ScrapeConfig(
                        asp=True,
                        js=js_code_template,
                        render_js=True,
                        rendering_wait=5500,
                        proxy_pool='public_datacenter_pool',
                        url="https://www.spyfly.com",
                    )
                )

                user_responses.append(api_response)
            
            except requests.exceptions.ConnectionError:
                # There should be a logger here
                # SCRAPFLY_LOGGER.critical("There is no Internet connection!")
                pass
            except Exception as e:
                # There should be a logger here
                # DATA_TYPE_LOGGER.error(str(e))
                pass
        
        return user_responses

    def extract_data_from_html(self):
        data = []
        responses = self.do_search()

        count = 0
        for resp in responses:
            count += 1

            with open(f'page{count}.html', 'w') as afp:
                afp.write(resp.content)

            soup = BeautifulSoup(resp.content, 'html.parser')
            main_tbody = soup.find("tbody", attrs={"id": "table-body"})

            if not main_tbody:
                # There should be a logger here
                # DATA_TYPE_LOGGER.error("Could not find a user ")
                break

            all_trs = main_tbody.find_all('tr')

        
            for tr in all_trs:
                user_data = {}
                tds = tr.find_all('td')
                user_data["full_name"] = tds[0].h5.text.title()
                user_data["age"] = tds[1].text

                location = str(tds[2]).replace('<td>', '').replace('</td>', '').split('<br/>')
                location.remove('')
                user_data["location"] = location

                relatives = str(tds[3]).replace('<td>', '').replace('</td>', '').split('<br/>')
                relatives.remove('')
                user_data["relatives"] = relatives

                data.append(user_data)

        return data


if __name__ == "__main__":
    TEST_USERS:tuple = (
    {
        "first_name": 'Kiran', 
        "last_name":'Rao', 
        "city":'New York', 
        "state": "CALIFORNIA"
    },
    {
        "first_name": 'James', 
        "last_name":'Hoffman', 
        "city":'Boston', 
        "state": "GEORGIA"
    },
    {
        "first_name": 'Jhon', 
        "last_name":'Jhonson', 
        "city":'New York', 
        "state": "MAINE"
    },
    {
        "first_name": 'William', 
        "last_name":'Hopkins', 
        "city":'New York', 
        "state": "NEW YORK"
    },
)

    spyfly = SpyFly(TEST_USERS)
    spyfly_json_data = spyfly.extract_data_from_html()

    with open('spyfly.json', 'w') as spyflyer:
        json.dump(spyfly_json_data, spyflyer, ensure_ascii=False, indent=4)