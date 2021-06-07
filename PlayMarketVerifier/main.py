# Standard library imports

# Third party imports
from aiogram import executor
from aiogram.bot import Bot
from aiogram.dispatcher import Dispatcher, storage
from aiogram.types import Message, CallbackQuery, ParseMode
import asyncio
import uvloop


from configs import BotStates, TOKEN, storage


uvloop.install()
loop = asyncio.get_event_loop()

bot = Bot(TOKEN, loop=loop)

dp = Dispatcher(bot=bot, loop=loop, storage=storage)


@dp.message_handler(commands=['start'], state='*')
async def start(message: Message):
    '''
        The first function that the User interacts with.
        After the User pressed the /start command - he will be offered to choose a language for interaction.
    '''

    await message.answer(
        text='Здравствуйте, чем могу помочь?')

    return await BotStates.start_state.set()


# @dp.callback_query_handler(state=BotStates.set_language)
# async def send_main_menu(call: CallbackQuery):
#     '''
#         As soon as User set the most comfortable language,
#         we send him buttons of main_menu and change Bot State.
#     '''
#     chat_id = call.message.chat.id

#     if call.data == 'ru':
#         await redworker.set_data(chat=chat_id, data='_ru')
#     else:
#         await redworker.set_data(chat=chat_id, data='_kg')

#     lang = await redworker.get_data(chat=chat_id)


#     return await BotStates.main_menu.set()


if __name__ == "__main__":
    executor.start_polling(
        dispatcher=dp,
        loop=loop
    )