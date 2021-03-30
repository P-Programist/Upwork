import uvloop
import aiohttp
import asyncio
import pathlib
import aiofiles
import pytesseract
from aiocsv import AsyncReader
from bs4 import BeautifulSoup as bs


PATH = pathlib.Path(__file__).parent

uvloop.install()


class Parser:
    def __init__(self, url, *args, **kwargs):
        super(Parser, self).__init__(*args, **kwargs)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive"
        }

        self.url = url

    async def get_html(self):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                request = await session.get(url=self.url)

                PHPSESSID = request.cookies.get('PHPSESSID').coded_value
                TS014f5480 = request.cookies.get('TS014f5480').coded_value

                self.headers["Cookie"] = f'TS014f5480={TS014f5480}; PHPSESSID={PHPSESSID};'
            except (
                    aiohttp.ClientError,
                    aiohttp.http_exceptions.HttpProcessingError):

                request = await session.get(url=self.url)

            return await request.text()

    async def extract_captcha_link(self, html):
        root = bs(html, 'html.parser')
        captcha_block = root.find('div', class_='form-row')
        captcha_link = captcha_block.img['src']
        return self.url + captcha_link

    async def get_captcha_path(self, captcha_link):
        captcha_img_path = f'{PATH}/captcha_img.png'

        async with aiohttp.ClientSession(headers=self.headers) as session:
            r = await session.get(url=captcha_link)
            async with aiofiles.open(captcha_img_path, mode='wb') as img:
                await img.write(await r.content.read())

            return captcha_img_path

    async def get_captcha_text(self, captcha_link):
        captcha_path = await self.get_captcha_path(captcha_link)
        text = pytesseract.image_to_string(captcha_path)
        return text

    async def get_token(self, html):
        root = bs(html, 'html.parser')
        token_row = root.find('input', attrs={"name": "token"})
        token = token_row['value']
        return token

    async def get_person_tables(self, ic, captcha, token):
        data = {
            "ic": ic,
            "captcha": captcha,
            "token": token
        }

        async with aiohttp.ClientSession(headers=self.headers) as session:
            request = await session.post(url=self.url, data=data)
            return await request.text()

    async def extract_data_from_tables(self, html):
        data = {}
        root = bs(html, 'html.parser')
        tables = root.find_all('table')

        try:
            first_table_fields = tables[0].find_all('td')
            second_table_fields = tables[1].find_all('td')
        except IndexError:
            return []

        data["nama_penuh"] = first_table_fields[0].text
        data["no_kad_pengenalan"] = first_table_fields[1].text
        data["tarikh_lahir"] = first_table_fields[2].text
        data["jantina"] = first_table_fields[3].text

        data["lokaliti"] = second_table_fields[0].text
        data["daerah_mengundi"] = second_table_fields[1].text
        data["dun"] = second_table_fields[2].text
        data["parlimen"] = second_table_fields[3].text
        data["negeri"] = second_table_fields[4].text

        return data

    async def upload_data(self, csv_file_path):
        html = await self.get_html()
        try:
            async with aiofiles.open(csv_file_path, mode="r", encoding="utf-8") as afp:
                async for row in AsyncReader(afp):
                    await asyncio.sleep(1)
                    while True:
                        await asyncio.sleep(1)
                        token = await self.get_token(html)
                        link = await self.extract_captcha_link(html)
                        captcha_text = await self.get_captcha_text(link)
                        if len(captcha_text) == 5:
                            captcha = captcha_text[:3]
                            person_data = await self.get_person_tables(row[0], captcha, token)

                            tables_data = await self.extract_data_from_tables(person_data)

                            if not tables_data:
                                token = await self.get_token(html)
                                link = await self.extract_captcha_link(html)
                                captcha_text = await self.get_captcha_text(link)
                                if len(captcha_text) == 5:
                                    captcha = captcha_text[:3]
                                    person_data = await self.get_person_tables(row[0], captcha, token)

                                    tables_data = await self.extract_data_from_tables(person_data)
                            break


        except FileNotFoundError:
            print('File not found! Try again...')


if __name__ == "__main__":
    parser = Parser('https://pengundi.spr.gov.my')
    path_to_csv = input('Type the full path to a CSV file: ')
    while '.csv' not in path_to_csv:
        path_to_csv = input('Type the full path to a CSV file: ')

    asyncio.run(parser.upload_data(path_to_csv))

    
