# Bot name: PlayMarketVerifier1Bot
# Bot link: t.me/PlayMarketVerifier1Bot

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.redis import RedisStorage2


TOKEN = '1738900776:AAHsAFuASXe4WcjCkjAWsrTxoEdYy9IUK9g'


storage = RedisStorage2(
    host='localhost',
    db=1,
    port=6379
)


class BotStates(StatesGroup):
    start_state = State()
    wait_for_a_link_state = State()
    check_availability = State()