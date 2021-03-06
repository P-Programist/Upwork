# Importing dependecies
import asyncio
import aiohttp
import uvloop
import aiofiles
import re
import pathlib
from bs4 import BeautifulSoup as bs
from aiocsv import AsyncWriter


uvloop.install()

PATH_TO_SCRIPT = pathlib.Path(__file__).parent

# Headers are need to avoid blocking from site where are you make requests to.

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0', 
    'Accept-Encoding': 'gzip, deflate, br', 
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 
    'Connection': 'keep-alive'
}

async def fetch_links_for_parsing(url):
    """The function take an URL to make request to and get list of links."""

    # Here we set a template that we are looking for.
    # For instance, we need to get every single link which locates between <loc>...</loc>
    # (.*?) -> is responsible for
    template = re.compile("<loc>(.*?)</loc>")

    # Create a session for HTTP requests.
    async with aiohttp.ClientSession(headers=HEADERS) as session:

        # Due to the session we make a request to the site where all links to parse are stored.
        async with session.get(url=url) as response:

            # Extracting data from response.
            data = await response.text()

            # Here we look for the template of URL which lies between <loc></loc>
            links = template.findall(data)

            # We open file to write there all those links which we are going to parse.
            async with aiofiles.open(str(PATH_TO_SCRIPT) + '/urls.txt', 'w') as f1:
                for link in links:
                    await f1.write(link+'\n')



async def fetch_html(url: str, session: aiohttp.ClientSession):
    """This function just make a request to a site to get HTML code 
        and pass it farther to the 'parse_html' function."""

    # The line below is specially for stopping the script as it may break a site by multiple requests.
    await asyncio.sleep(1.5)

    # These two lines are responsible for asking HTML data from site.
    async with session.get(url) as response:
        data = await response.text()

    return data



async def parse_html(url: str):
    """When this function is called data comes inside the function 
        it parses and returns tuple of 2 objects: BRAND and CASHBACK.
        In the end, function will return a tuple that consists of two values: BRAND and BRAND CASHBACK    
    """

    async with aiohttp.ClientSession(headers=HEADERS) as session:

        # The line below stores HTML code.
        html = await fetch_html(url, session) # This function is above function.

        # As soon as we GET HTML code we pass it for parsing into BEAUTIFULSOUP4.
        soup = bs(html, 'html.parser')

        # Some pages do not have neither brand name nor cashback info.
        # Since that we take this construction into TRY: EXCEPT: construction.
        try:
            brand = soup.find('span', class_='gecko-merchant-heading').text # Here we extract brand name
            brand_cashback = soup.find('span', class_='cashback-desc').text[:-1] # Here we extract brand cashback

            return brand, brand_cashback

        except AttributeError as AE:
            return None



async def write_data_to_csv():
    """
    This function is more about asynchronization than functionality.
    From the very beginning the architecture has been made for asynchronous behaviour.
    So, one of the entry points is HERE.
    """

    tasks = []
    
    # We load the file that keeps all URLS that we need to visit and parse.
    # So, we take one by one and pass it to functions above.
    async with aiofiles.open(str(PATH_TO_SCRIPT) + '/urls.txt', 'r') as f3:
        urls = await f3.readlines()
        for url in urls:
            tasks.append(
                asyncio.create_task(
                    parse_html(
                        url.strip('\n')
                        )
                )
            )

    # After all functions that we wrote before will made their job,
    # the result will be stored in a list that we assign to OUTPUT variable.

    # This list consists of tuple which in its turn consists of two values: BRAND and BRAND CASHBACK
    output = await asyncio.gather(*tasks)

    # Here we create a new CSV file to write down our results.
    async with aiofiles.open(str(PATH_TO_SCRIPT) + '/cashbacks.csv', 'w+') as f2:
        writer = AsyncWriter(f2)
        await writer.writerow(('Company', 'Cashback'))

        # The loop below write one by one line into CSV file
        for row in output:
            if row:
                await writer.writerow(row)



async def main():
    """
    Before everything will start we need to get URLS that we want to parse.
    Specialy for this project all URLS were kept on another site, 
    so we needed to extract these addresses first and only then start to visit them.

    In case, You will have the same situation with URLS where You need to EXTRACT them first and then to proceed,
        all You need just ot replace them as those two below.

    If You do not need to extract URLS from another site at all and You have them just stored in a file,
        rename this file as urls.txt and put this file right next to this script.
    
    The script itsef will find urls.txt extract links from there and make requests.
    """

    # Delete these lines if You have separated urls.txt file OR leave it as it is just replace links inside fetch_links_for_parsing() function.
    #######################################################################################################
    task1 = asyncio.create_task(fetch_links_for_parsing('https://www.topcashback.com/merchantslinks1.xml'))
    task2 = asyncio.create_task(fetch_links_for_parsing('https://www.topcashback.com/merchantslinks2.xml'))

    await asyncio.gather(task1, task2)
    #######################################################################################################


    await write_data_to_csv()


if __name__ == "__main__":
    # The MAIN ENTRY POINT!
    asyncio.run(main())