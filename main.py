from globals import *
import requests
import json
import random
import asyncio

START_KB.add(ST_B1, ST_B2, ST_B3)

LANG_KB.add(LANG_B1, LANG_B2)

GAME_KB.add(GM_B1, GM_B2)

class ClientStatesGroup(StatesGroup):
    not_playing = State()
    select_language = State()
    wait_letter = State()


async def send_text(usr_id, text, keyboard):
    """
    This function sends a message to the user
    and also sets the required keyboard.
    :param usr_id: User's ID
    :param text: Text of the message
    :param keyboard: Required keyboard
    :return: nothing
    """
    await bot.send_message(chat_id=usr_id, text=text, reply_markup=keyboard)


def GetEnglishWord():
    """
    This function accesses the random
    English word generation site API and
    returns a random English noun.
    :return: Random English noun
    """
    response = requests.get(WORD_GENERATE_URL)
    response = response.json()
    word = response[0].upper()
    return word


def GetRussianWord():
    """
    This function takes a random Russian noun
    from the file "russian_nouns.txt" and returns it.
    :return: Random Russian noun
    """
    with open('russian_nouns.txt', 'r') as file:
        words = file.readlines()
    random_word = random.choice(words).strip()
    random_word = random_word.upper()
    return random_word


def GetDefinition(word, language='en'):
    """
    This function calls the ChatGPT API with a request
    to generate a short description of a given word
    in a riddle format in a given language.
    The function then returns this description.
    :param word: The word to which we need to generate a description
    :param language: The language of the description of the word
    :return: Description of a given word in a given language
    """
    prompt = f"Q: You must describe the word \"{word}\" very briefly (for riddling it to another person), no more than 10 words.\nA:"
    if language == 'rus':
        prompt = f"Q: You must describe the word \"{word}\" very briefly (for riddling it to another person), no more than 10 words. Answer in russian.\nA:"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\n"]
    )
    answer = response["choices"][0]["text"]
    answer = answer[1:-1]
    return answer


def start_game(usr_id):
    """
    This function sets the initial required data for the game session
    :param usr_id: User's ID
    :return: nothing
    """
    users_data[usr_id]['input'] = ''
    get_word = GetRussianWord if users_data[usr_id]['language'] == 'rus' else GetEnglishWord
    word = get_word()
    while len(word) > 7:
        word = get_word()
    users_data[usr_id]['word'] = word
    users_data[usr_id]['is_win'] = False
    users_data[usr_id]['lifes'] = 6
    users_data[usr_id]['used_letters'] = []
    users_data[usr_id]['mask'] = ('_' + ' ') * len(word)
    users_data[usr_id]['mask'] = users_data[usr_id]['mask'][:-1]
    definition = GetDefinition(word.lower(), users_data[usr_id]['language'])
    users_data[usr_id]['definition'] = definition


@disp.message_handler(commands=['start'], state=None)
async def start_command(message: types.Message):
    """
    This function handles the user command "/start", which starts the bot.
    :param message: "/start" command
    :return: nothing
    """
    usr_id = message.from_user.id
    if usr_id not in users_data:
        users_data[usr_id] = dict()
    await ClientStatesGroup.not_playing.set()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f'Hi, {message.from_user.first_name}! Here you can play in Hangman game!',
                           reply_markup=START_KB,
                           parse_mode='HTML')


@disp.message_handler(commands=['help'], state=ClientStatesGroup.not_playing)
async def help_command(message: types.Message, state: FSMContext):
    """
    This function handles the user command "/help",
    which sends command information to the user.
    :param message: "/help" command
    :param state: Current state of the bot
    :return: nothing
    """
    await bot.send_message(chat_id=message.from_user.id,
                           text=HELP_TEXT,
                           reply_markup=START_KB,
                           parse_mode='HTML')


@disp.message_handler(commands=['description'], state=ClientStatesGroup.not_playing)
async def description_command(message: types.Message):
    """
    This function handles the user command "/description",
    which sends a description of the bot to the user.
    :param message: "/description" command
    :return: nothing
    """
    await bot.send_message(chat_id=message.from_user.id,
                           text=DESCRIPTION_TEXT,
                           reply_markup=START_KB,
                           parse_mode='HTML')


@disp.message_handler(commands=['play'], state=ClientStatesGroup.not_playing)
async def play_command(message: types.Message):
    """
    This function handles the user command "/play",
    which sets the keyboard for selecting the language of the target word.
    :param message: "/play" command
    :return: nothing
    """
    usr_id = message.from_user.id
    await ClientStatesGroup.next()
    await bot.send_message(chat_id=usr_id,
                           text='Choose the language of the hidden word',
                           reply_markup=LANG_KB,
                           parse_mode='HTML')


@disp.message_handler(commands=['en'], state=ClientStatesGroup.select_language)
async def select_en(message: types.Message, state: FSMContext):
    """
    This function handles the user command "/en",
    which starts the game with the word puzzled in English.
    :param message: "/en" command
    :param state: Current state of the bot
    :return: nothing
    """
    usr_id = message.from_user.id
    users_data[usr_id]['language'] = 'en'
    start_game(usr_id)
    await send_text(usr_id, "The game is started!\n", GAME_KB)
    text = f"Your word is:\n{users_data[usr_id]['definition']}\n{users_data[usr_id]['mask']}"
    photo = open(f'lifes_{users_data[usr_id]["lifes"]}.jpg', 'rb')
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=photo,
                         caption=text)
    await send_text(usr_id, 'Enter a letter or the whole word:\n', GAME_KB)
    await ClientStatesGroup.next()


@disp.message_handler(commands=['rus'], state=ClientStatesGroup.select_language)
async def select_rus(message: types.Message, state: FSMContext):
    """
    This function handles the user command "/rus",
    which starts the game with the word puzzled in Russian.
    :param message: "/rus" command
    :param state: Current state of the bot
    :return: nothing
    """
    usr_id = message.from_user.id
    users_data[usr_id]['language'] = 'rus'
    start_game(usr_id)
    await send_text(usr_id, "The game is started!\n", GAME_KB)
    text = f"Your word is:\n{users_data[usr_id]['definition']}\n{users_data[usr_id]['mask']}"
    photo = open(f'lifes_{users_data[usr_id]["lifes"]}.jpg', 'rb')
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=photo,
                         caption=text)
    await send_text(usr_id, 'Enter a letter or the whole word:\n', GAME_KB)
    await ClientStatesGroup.next()


@disp.message_handler(commands=['stop'], state=ClientStatesGroup.wait_letter)
async def stop_game_command(message: types.Message, state: FSMContext):
    """
    This function handles the user command "/stop",
    which stops the running game session.
    :param message: "/stop" command
    :param state: Current state of the bot
    :return: nothing
    """
    usr_id = message.from_user.id
    await send_text(usr_id, 'The game was stopped.\n', START_KB)
    await ClientStatesGroup.not_playing.set()


@disp.message_handler(commands=['hint'], state=ClientStatesGroup.wait_letter)
async def hint_command(message: types.Message, state: FSMContext):
    """
    This function handles the user command "/hint",
    which reveals a random letter of the hidden word to the user.
    :param message: "/hint" command
    :param state: Current state of the bot
    :return: nothing
    """
    usr_id = message.from_user.id
    random_letter = random.choice(users_data[usr_id]['word'])
    while random_letter in users_data[usr_id]['used_letters']:
        random_letter = random.choice(users_data[usr_id]['word'])
    users_data[usr_id]['used_letters'].append(random_letter)
    mask_list = list(users_data[usr_id]['mask'])
    for index in range(len(users_data[usr_id]['word'])):
        if users_data[usr_id]['word'][index] == random_letter:
            mask_list[index * 2] = random_letter
    users_data[usr_id]['mask'] = ''.join(mask_list)
    if users_data[usr_id]['mask'][::2] == users_data[usr_id]['word']:
        users_data[usr_id]['is_win'] = True
    if users_data[usr_id]['is_win']:
        await send_text(usr_id, f"Exactly! The word is {users_data[usr_id]['word']}", START_KB)
        await send_text(usr_id, 'Congratulations!!! You won in this game!\n', START_KB)
        await ClientStatesGroup.not_playing.set()
    else:
        text = f"Your word is:\n{users_data[usr_id]['definition']}\n{users_data[usr_id]['mask']}"
        photo = open(f'lifes_{users_data[usr_id]["lifes"]}.jpg', 'rb')
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=photo,
                             caption=text)
        await send_text(usr_id, 'Enter a letter or the whole word:\n', GAME_KB)


@disp.message_handler(state=ClientStatesGroup.wait_letter)
async def user_text(message: types.Message, state: FSMContext):
    """
    This function handles a text message sent by the user during the game.
    :param message: User's text message
    :param state: Current state of the bot
    :return: nothing
    """
    usr_id = message.from_user.id
    user_input = message.text.upper()
    if len(user_input) > 1 and user_input.isalpha():
        if user_input == users_data[usr_id]['word']:
            users_data[usr_id]['is_win'] = True
        else:
            users_data[usr_id]['lifes'] -= 1
            await send_text(usr_id, 'This is wrong word\n', GAME_KB)
    elif len(user_input) == 1 and user_input.isalpha():
        if user_input in users_data[usr_id]['used_letters']:
            await send_text(usr_id, "You have already used this letter\n", GAME_KB)
        elif user_input in users_data[usr_id]['word']:
            await send_text(usr_id, f"Great! You just opened new letter {user_input}\n", GAME_KB)
            users_data[usr_id]['used_letters'].append(user_input)
            mask_list = list(users_data[usr_id]['mask'])
            for index in range(len(users_data[usr_id]['word'])):
                if users_data[usr_id]['word'][index] == user_input:
                    mask_list[index * 2] = user_input
            users_data[usr_id]['mask'] = ''.join(mask_list)
            if users_data[usr_id]['mask'][::2] == users_data[usr_id]['word']:
                users_data[usr_id]['is_win'] = True
        else:
            users_data[usr_id]['lifes'] -= 1
            await send_text(usr_id, f"I'm sorry, but there is no letter \'{user_input}\' in the word(\n", GAME_KB)
            users_data[usr_id]['used_letters'].append(user_input)
    else:
        await send_text(usr_id, "Your input must be letter or word!\n", GAME_KB)
    if users_data[usr_id]['is_win']:
        await send_text(usr_id, f"Exactly! The word is {users_data[usr_id]['word']}", START_KB)
        await send_text(usr_id, 'Congratulations!!! You won in this game!\n', START_KB)
        await ClientStatesGroup.not_playing.set()
    elif users_data[usr_id]['lifes'] == 0:
        text = f"""
        Sorry, but you have been cocknut)))\n
        The hidden word is: {users_data[usr_id]['word']}
        """
        photo = open(f'lifes_{users_data[usr_id]["lifes"]}.jpg', 'rb')
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=photo,
                             caption=text,
                             reply_markup=START_KB)
        await ClientStatesGroup.not_playing.set()
    else:
        text = f"Your word is:\n{users_data[usr_id]['definition']}\n{users_data[usr_id]['mask']}"
        photo = open(f'lifes_{users_data[usr_id]["lifes"]}.jpg', 'rb')
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=photo,
                             caption=text)
        await send_text(usr_id, 'Enter a letter or the whole word:\n', GAME_KB)


if __name__ == '__main__':
    executor.start_polling(disp, skip_updates=True)

