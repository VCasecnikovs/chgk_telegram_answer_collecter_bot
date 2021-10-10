from telebot import types

def get_register_keyboard():
    register_markup = types.ReplyKeyboardMarkup()
    register_button = types.KeyboardButton("Зарегистрироваться")
    register_markup.add(register_button)
    return register_markup