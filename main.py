import types
from typing import Dict, List
import telebot
import config
import keyboards
from game_master import GameStatus, GameMaster
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

def get_user_status(msg: telebot.types.Message):
    return user_status_dict.get(msg.from_user.id)

def set_user_status(msg: telebot.types.Message, user_status : USER_STATUS):
    user_status_dict[msg.from_user.id] = user_status

@bot.message_handler(commands=["start"])
def welcome_tne_newcomer(msg):
    bot.reply_to(msg, "Привет, этот бот позволяет удобно сдавать ответы на ЧГК событиях, особенно в это нелёгкое ковидное время. Если ты капитан, ты можешь зарегестрировать свою комманду, для этого напиши /register")


@bot.message_handler(commands=["register"])
def start_registration_process(msg : telebot.types.Message):
    if gm.status == GameStatus.IN_GAME:
        bot.reply_to(msg, "К сожалению, сейчас уже проходит игра")
        return

    if gm.status == GameStatus.IDLE:
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

    
@bot.message_handler(commands=["start_registration"])
def start_registration(msg):
    if get_user_status(msg) == USER_STATUS.GAMEMASTER:
        gm.start_registration()
        bot.reply_to(msg, "Регистрация начата")


bot.infinity_polling()