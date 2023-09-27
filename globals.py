from constants import *
from aiogram import Bot, Dispatcher, types, executor
import openai
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

openai.api_key = "Your openai key"

storage = MemoryStorage()
bot = Bot(TOKEN_API)
disp = Dispatcher(bot=bot,
                  storage=storage)

users_data = dict()

