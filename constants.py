from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text

TOKEN_API = 'Your telegram bot key'
WORD_GENERATE_URL = 'https://random-word-form.herokuapp.com/random/noun'

START_KB = ReplyKeyboardMarkup(resize_keyboard=True)
ST_B1 = KeyboardButton('/help')
ST_B2 = KeyboardButton('/description')
ST_B3 = KeyboardButton('/play')

LANG_KB = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
LANG_B1 = KeyboardButton('/en')
LANG_B2 = KeyboardButton('/rus')

GAME_KB = ReplyKeyboardMarkup(resize_keyboard=True)
GM_B1 = KeyboardButton('/stop')
GM_B2 = KeyboardButton('/hint')

HELP_TEXT = """
Here is a commands list:

<b>/start</b> - <em>Bot\'s start</em>
<b>/help</b> - <em>Commands list</em>
<b>/description</b> - <em>Bot\'s description</em>
<b>/play</b> - <em>Start the game</em>
<b>/hint</b> - <em>Get one letter from the hidden word</em>
"""

DESCRIPTION_TEXT = """
Hi, I'm a bot designed to play <b>Hangman</b>.

The <b>rules</b> of the game are very simple:
You have to <b>guess</b> the letters of the given word. Each correctly guessed letter will reveal a hidden word. If you have not guessed all the letters yet, but think you already know the word, you can try to guess the <b>whole word</b>. But <b>remember</b>, every wrong answer makes you closer and closer to losing.
"""
