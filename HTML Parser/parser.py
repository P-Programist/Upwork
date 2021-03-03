import os
from loggers import logger
from transliterate import translit
from bs4 import BeautifulSoup as BS


# There are some data which does not have any data inside, however, still presents in global scope and breaks the script.
garbish = ('Нам нужна', 'фото', 'база') 


class MainScraper:
    '''
        This class is responsible for Scraping "dataset" folder for extracting specific information based on requirements.
        The Requirements are the following:
            The data is organized per month: August to February

            Each "month" directory contains a file called "messages.html"
            (see screenshot1.jpg)

            messages.html is a loose collection referencing text, images and videos. Each "paragraph" (<div class="from_name">) is dedicated to a person.
            Note that the text is in Cyrillic(likely Unicode).

            Need an HTML parser to parse messages.html and perform the following:
            1)For each person referenced, extract first/last name (it's between <strong> and </strong>, see screenshot2.jpg)
            1a) Transliterate using for example pyhton translit package and replace spaces with _:
            In other words, "Иванов Иван Иванович" becomes "Ivanov_Ivan_Ivanovich"
            2)Create a directory for this person, for example:
            _Kubrakov_Ivan_Vladimirovich
            3)Extract image in the title and save it in the directory above (all images are likely stored under "images" in the directory structure above) (see screenshot3.jpg)
            4)Extract all other images or videos referenced in <div class="from_name"> and save it in the directory created in 2)
            5)In the directory created in 2) create a file called "info.html"
            6)All html in inner <div class="text"> should be saved in "info.html"
            (see screenshot4.jpg)
            6a) The resulting directory should be similar to screenshot5.jpg
            7)Repeat for each person referenced
            8)Repeat for each month.
    '''

    def __init__(self, filename) -> None:
        '''The __init__ method is responsible for keeping some constant variables to configure the path to DATASET.'''

        self.PERSON_PATH = None
        self.PATH = os.path.dirname(__file__) + f'/{filename}/'
        
    
    def main(self):
        '''This function splits data into pieces and prepares it for saving in directories.'''
        if not os.path.exists(self.PATH):
            return 'Filename is not correct, please check the spelling!'

        for directory in os.listdir(self.PATH):
            try:
                with open(self.PATH + directory + '/messages.html', 'r') as messages:
                    soup = BS(messages, 'html.parser')
            except FileNotFoundError as fee:
                logger.warning(fee)


            body_blocks = soup.find_all('div', class_='body')

            if not os.path.exists(os.path.dirname(__file__) + f'/data/{directory}/persons/'):
                os.makedirs(os.path.dirname(__file__) + f'/data/{directory}/persons/')

            for block in body_blocks[1:]:

                media_block = block.find('div', class_='media_wrap clearfix')
                main_div = block.find('div', class_='text')

                if main_div:
                    # In order to save text as in indictment.txt example we take it as it is.
                    div_with_class_text = BS(main_div.prettify(), 'html.parser')

                    if not div_with_class_text.get_text().strip().split('\n')[0].startswith(garbish[0]):
                        raw_name = div_with_class_text.get_text().strip().split('\n')[0].replace(' ', '_').strip(',')
                        if raw_name.count('_') == 0:
                            raw_name = ''.join(div_with_class_text.get_text().strip().split('\n')[:4]).replace(' ', '_').replace('__', '_').strip(',')


                        # This code is responsible for checking the name of person.
                        # If name starts from forbidden words which do not have any information the name will be skipped.
                        if garbish[1] not in raw_name.lower() and garbish[2] not in raw_name.lower():
                            if '-' in raw_name:
                                name = '_' + translit(raw_name.split('-')[0], 'ru', reversed=True).title()
                            else:
                                name = '_' + translit(raw_name, 'ru', reversed=True).title()


                            self.PERSON_PATH = os.path.dirname(__file__) + f'/data/{directory}/persons/' + name

                            if len(name) > 50:
                                self.PERSON_PATH = os.path.dirname(__file__) + f'/data/{directory}/persons/' + name[:60]

                        self.create_directories(self.PERSON_PATH)


                '''When the data is ready to be saved, this part gets both a path and data to save which.'''
                if media_block and self.PATH is not None:
                    try:
                        # This code creates "indictment.txt" in every person's folder.
                        with open(self.PERSON_PATH + '/indictment.txt', 'w') as indictment:
                            indictment.write(div_with_class_text.get_text().strip('\n').replace('\n\n', ''))


                        # This code creates "info.txt" in every person's folder
                        with open(self.PERSON_PATH + '/info.html', 'w') as info:
                            info.write(str(div_with_class_text))



                        # This code extracts both photos and videos that related to the person
                        with open(self.PATH + directory + '/' + media_block.a["href"], 'rb') as media_file1:
                            media_file_data = media_file1.read()


                        # This code extracts only images that related to the person
                        with open(self.PATH + directory + '/' + media_block.a.img["src"], 'rb') as media_file2:
                            media_file_data = media_file2.read()



                        # This code saves both photos and videos that related to the person
                        with open(self.PERSON_PATH + '/' + media_block.a["href"].split('/')[1], 'wb') as person_media_file1:
                            person_media_file1.write(media_file_data)


                         # This code saves only images that related to the person
                        with open(self.PERSON_PATH + '/' + media_block.a.img["src"].split('/')[1], 'wb') as person_media_file2:
                            person_media_file2.write(media_file_data)

                    except FileNotFoundError as fee:
                        logger.warning(fee)
                        
                    except OSError as ose:
                        logger.warning(ose)



    def create_directories(self, path_to_create):
        '''The function creates the same named directories as were parsed from the beginning.'''
        try:
            os.mkdir(path_to_create)

        except FileExistsError as fee:
            logger.warning(fee)

        except OSError as ose:
            logger.warning(ose)



main_scraper = MainScraper(input('What is name of the folder: '))
print(main_scraper.main())
