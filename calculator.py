import math

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from IOData import save_static, load_static
from emoji import emojize as e
import logging, mytoken

logging.basicConfig(filename='bot.log', 
                    filemode='w',
                    encoding="utf-8",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

"""Логирование в нужном формате в bot.log с модификатором перезаписи. """ 

logger = logging.getLogger(__name__)

START_MESSAGE = """Запишите выражение, ответ на которое, тебя интересует"""

HELP_MESSAGE = """Это просто калькулятор. Отправь выражение, а он вернет тебе его результат.

***Операторы***:
    + - сложение;
    - - вычитание;
    \* - умножение;
    / - деление;
    \*\* - возведение в степнь.
    
***Функции***:
    cos(x) - косинус x;
    sin(x) - синус x;
    tg(x) - тангенс x;
    fact(x) - факториал x;
    sqrt(x) - квадратный корень х;
    sqr(x) - х в квадрате.

***Логарифмы***:
    log2(x) - логарифм х по основанию 2;
    lg(х) - десятичный логарифм х;
    ln(x) - натуральный логарифм x;
    log(b, х) - логарифм х по основанию b;

***Системы счисления***:
    0bx - перевести двоичное число х в десятичное;
    0ox - перевести восьмиричное число х в десятичное;
    0xx - перевести шестнадцатиричное число х в десятичное;"""

pi = 3.141592653589793238462643

def fact(float_):
    return math.factorial(float_)

def cos(float_):
    return math.cos(float_)

def sin(float_):
    return math.sin(float_)

def tg(float_):
    return math.tan(float_)
    
def tan(float_):
    return math.tan(float_)

def ln(float_):
    return math.log(float_)

def log(base, float_):
    return math.log(float_, base)

def lg(float_):
    return math.log10(float_)

def log2(float_):
    return math.log2(float_)

def exp(float_):
    return math.exp(float_)

def start_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.from_user
    logger.info(f"User {name.first_name} started calculator.")

