import asyncio
import aiohttp
import aiofiles
import pandas as pd
import pathlib
from bs4 import BeautifulSoup as bs
import json
from aiocsv import AsyncWriter

PATH = pathlib.Path(__file__).parent

xlsx_path = str(PATH) + '/data.xlsx'
 
data = pd.read_excel(xlsx_path)

links = data['URL'].tolist()[24:]


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Content-Type": "text/plain;charset=UTF-8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}


async def get_html(url):
    await asyncio.sleep(2.1)
    async with aiohttp.ClientSession(headers=HEADERS) as s_1:
        request = await s_1.get(url)
        response = await request.text()
        return response


async def extract_data(html):
    result = {}

    soup = bs(html, 'html.parser')

    company_name = soup.find('b', class_='inline-block')

    if company_name:
        result.update({'CompanyName': company_name.text})
    else:
        return {}

    overview_block = soup.find('div', attrs={"id": "profile-content-container"})
    
    highlights = overview_block.find_all('div', class_='flex mb-10')

    for highlight in highlights:
        text_list = [item for item in highlight.text.split('\n') if item]
        result.update({f"Highlight{text_list[0]}": text_list[-1]})

    team_section = overview_block.find('div', class_='flex flex-row flex-wrap')

    team_members = team_section.find_all('div', class_='flex w-full mb-12')

    member_count = 1

    for team_member in team_members:
        team_member_block = team_member.find('div', class_='flex flex-col justify-center').div
        team_member_properties = json.loads(team_member_block['data-react-props'])
       
        result.update({f"MemberName{member_count}": team_member_properties.get('userFullName')})
        result.update({f"MemberPosition{member_count}": team_member_properties.get('userTitle')})
        result.update({f"MemberBio": team_member_properties.get('userBio')})
        member_count += 1

    return result


async def save_data(data):
     async with aiofiles.open(
        file=str(PATH) + "/data.csv", mode="a", 
        encoding="utf-8", newline="") as afp:
        
        writer = AsyncWriter(afp, dialect="unix")

        # await writer.writerow(
        #     [
        #         "CompanyName", 

        #         "Highlight1", "Highlight2", "Highlight3", 
        #         "Highlight4", "Highlight5", "Highlight6", 

        #         "MemberName1", "MemberPosition1", "MemberBio1", 
        #         "MemberName2", "MemberPosition2", "MemberBio2", 
        #         "MemberName3", "MemberPosition3", "MemberBio3", 
        #         "MemberName4", "MemberPosition4", "MemberBio4", 
        #         "MemberName5", "MemberPosition5", "MemberBio5", 
        #         "MemberName6", "MemberPosition6", "MemberBio6"
        #     ]
        # )

        
        row_data = []
        row_data.append(data.get('CompanyName'))

        for i in range(1, 7):
            row_data.append(data.get(f'Highlight{i}'))

        for i in range(1, 7):
            row_data.append(data.get(f'MemberName{i}'))
            row_data.append(data.get(f'MemberPosition{i}'))
            row_data.append(data.get(f'MemberBio{i}'))

        await writer.writerow(row_data)


def main():
    for link in links:
        html = asyncio.run(get_html(link))
        data = asyncio.run(extract_data(html))
        asyncio.run(save_data(data))
        


# if __name__ == "__main__":
#     main()

