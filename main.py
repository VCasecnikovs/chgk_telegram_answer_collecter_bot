import time
from typing import Dict, List, Union
import telebot
import config
from game_master import GAME_STATUS, GameMaster
from enum import Enum

from teams import Team

class USER_STATUS(Enum):
    NEWCOMER = 0
    CAPTAIN = 1
    ENTERING_CODE = 2
    ENTERING_TEAM_NAME = 3
    GAMEMASTER = 4

bot = telebot.TeleBot(config.TOKEN)
gm = GameMaster()
user_status_dict = {config.GAMEMASTER_TELEGRAM_ID : USER_STATUS.GAMEMASTER}

teams : Dict[int, Team] = {}
answers: Dict[int, str] = {}

def get_user_status(msg: telebot.types.Message):
    return user_status_dict.get(msg.from_user.id)

def set_user_status(msg: telebot.types.Message, user_status : USER_STATUS):
    user_status_dict[msg.from_user.id] = user_status

@bot.message_handler(commands=["start"])
def welcome_tne_newcomer(msg):
    bot.reply_to(msg, "Привет, этот бот позволяет удобно сдавать ответы на ЧГК событиях, особенно в это нелёгкое ковидное время. Если ты капитан, ты можешь зарегестрировать свою комманду, для этого напиши /register")


@bot.message_handler(commands=["register"])
def start_registration_process(msg : telebot.types.Message):
    if gm.status == GAME_STATUS.IN_GAME:
        bot.reply_to(msg, "К сожалению, сейчас уже проходит игра")
        return

    if gm.status == GAME_STATUS.IDLE:
        bot.reply_to(msg,"К сожалению, сейчас не открыта регистрация")
        return

    bot.reply_to(msg, "Напиши секретное слово (мы используем секретное слово, чтобы только коммандиры могли регестрировать команды)")
    set_user_status(msg, USER_STATUS.ENTERING_CODE)

@bot.message_handler(func=lambda msg: get_user_status(msg) == USER_STATUS.ENTERING_CODE)
def check_code(msg: telebot.types.Message):
    if msg.text == config.SECRET_CODE:
        bot.reply_to(msg, "Правильный код, теперь введите название комманды")
        set_user_status(msg, USER_STATUS.ENTERING_TEAM_NAME)
    else: 
        bot.reply_to(msg, "Вы ввели неверный код")
        set_user_status(msg, USER_STATUS.NEWCOMER)

@bot.message_handler(func=lambda msg: get_user_status(msg) == USER_STATUS.ENTERING_TEAM_NAME)
def set_command_name(msg: telebot.types.Message):
    team = Team(name=msg.text, captain_id=msg.from_user.id)
    teams[msg.from_user.id] = team
    set_user_status(msg, USER_STATUS.CAPTAIN)
    bot.reply_to(msg, f"Вы успешно зарегистрировались как капитан. Удачи, {msg.text}!")

    
@bot.message_handler(commands=["start_registration"], func=lambda  msg: get_user_status(msg) == USER_STATUS.GAMEMASTER)
def start_registration(msg):
    gm.start_registration()
    bot.reply_to(msg, "Регистрация начата")

@bot.message_handler(commands=["start_game"], func=lambda  msg: get_user_status(msg) == USER_STATUS.GAMEMASTER)
def start_game(msg):
    gm.start_game()
    bot.reply_to(msg, "Игра начата")
    for captain_id in teams.keys():
        bot.send_message(captain_id, "Игра началась, после озвучивания вопроса, вам придёт сообщение о том, что вы можете отвечать на вопрос. Ответ пишите текстом этому боту. Удачи!")

@bot.message_handler(func=lambda msg: get_user_status(msg) == USER_STATUS.CAPTAIN and gm.status == GAME_STATUS.ANSWERS_COLLECTION)
def collect_answer(msg : telebot.types.Message):
    if answers.get(msg.from_user.id):
        bot.reply_to(msg, f"Ваш ответ изменён на последний вами сданный {answers[msg.from_user.id]} => {msg.text} ")
    else: 
        bot.reply_to(msg, f"Ваш ответ ->{msg.text}<- получен")
    answers[msg.from_user.id] = msg.text

@bot.message_handler(commands=["allow_answering"], func=lambda  msg: get_user_status(msg) == USER_STATUS.GAMEMASTER)
def start_answers_collection(msg):
    gm.start_answers_collection()
    bot.reply_to(msg, "Начат сбор ответов")
    for captain_id in teams.keys():
        bot.send_message(captain_id, f"Вы можете отвечать")
    
@bot.message_handler(commands=["end_answers_collection"], func=lambda  msg: get_user_status(msg) == USER_STATUS.GAMEMASTER)
def end_answers_collection(msg: Union[telebot.types.Message, None], time_left_seconds: int = 10):
    bot.reply_to(msg, f"Начат обратный отчёт")
    for captain_id in teams.keys():
        bot.send_message(captain_id, f"Осталось {time_left_seconds} до сдачи ответа")
    time.sleep(time_left_seconds)
    gm.end_answers_collection()
    for captain_id in teams.keys():
        answer = answers.get(captain_id)
        if answer:
            bot.send_message(captain_id, f"Ваш ответ: {answers.get(captain_id)}")
        else: 
            bot.send_message(captain_id, "Мы так и не дождались ответа")
    bot.reply_to(msg, f"Получены такие ответы {answers}")
    answers.clear()

bot.infinity_polling()