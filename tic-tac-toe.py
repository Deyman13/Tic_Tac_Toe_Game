# Встроенные библиотеки Python, а так же модули других файлов
import logging, mytoken
import datetime
from random import randint as rnd
from IOData import save_static, load_static

# Установленные извне библиотеки
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from emoji import emojize as e



logging.basicConfig(filename='bot.log', 
                    filemode='w',
                    encoding="utf-8",
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

"""Логирование в нужном формате в bot.log с модификатором перезаписи. """ 

logger = logging.getLogger(__name__)
 

# Константы в пайтон объявляются в верхнем регистре. 

TOKENEMP = e(":gift:", language="alias")

"""Пустая ячейка игрового поля (подарочная коробочка)"""



TOKENBOT = e(":star2:", language="alias")

"""Ячейка игрового поля, заполненная ботом (звездочка)"""



TOKENPLAYER = e(":snowflake:", language="alias")

"""Ячейка игрового поля, заполненная пользователем (снежинка)"""



ANSWER_SPLIT = (f'{e(":trophy:", language="alias")} Рейтинг {e(":trophy:", language="alias")}',
                 'Побед: ', 
                 'Поражений: ')

"""Статистика пользователя, включающая победы и поражения в виде рейтинга.

    Формат: (Рейтинг, Побед, Поражений)"""



STATISTICS_EMPTY = {'win': 0, 'lost': 0, 'lastgame': None}

"""Начальная статистика:

    Формат - {Побед: 0, Поражений: 0, Последняя игра: None} """



FIELD_EMPTY = (list(map(str, range(0, 9))))

"""Cписок чисел от 0 до 8, приведенных к строчному типу, для итерации по полю.

    Формат - ['0', '1', '2', '3', '4', '5', '6', '7', '8']"""



WINS_LINE = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
             (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

"""Cписок кортежей победных комбинаций по которым определяется победа

    Формат - [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6)]"""



VALID = "012345678"

"""Cтрока валидных значений для проверки незаполненных ячеек

    Формат: '012345678'"""



game_status = {}

"""Состояние поля у определенного пользователя по его ID"""



game_status_keys = game_status.keys()

"""Переменная ключей словаря состояния"""



game_static = {}

"""Статистика определенного пользователя по его ID"""



game_static_keys = game_static.keys()

"""Переменная ключей словаря статистики"""



def check_status(id_user: int):
    """Функция для проверки статистики пользователя и текущего состояния его поля

    - В случае, если пользователь новый - ему дается пустое поле и нулевая статистика
    - В случае, если пользователь уже играл - загружается его статистика и пустое поле"""
 
    if id_user not in game_static_keys:

        # Статусу поля пользователя присваивается копия нового поля (копия для того, чтобы не изменять константу пустого поля)
        game_status[id_user] = FIELD_EMPTY.copy()

        # При помощи функции load_static подгружается информация о статистике пользователя, или ее отсутствии (см. нотации функции)
        data = load_static()

        # Если у пользователя уже есть статистика и он не новый
        if str(id_user) in data.keys():

            # Статистике присваиваются значения прошлых достижений
            game_static[id_user] = data[str(id_user)]

        else: 
            # Иначе присваивается нулевая статистика 
            game_static[id_user] = STATISTICS_EMPTY.copy()

    # Отображение в терминале для контроля работы программы. На функционирование в телеграмм не влияет. 
    print(game_status) 
    print(game_static)



def builde_answer(id_user: int, strings: list):
    """Основное табло информации по текущему сеансу игры

    Показывает:
    Константы:
    - Рейтинг
    - Победы
    - Поражения

    Изменяемые параметры текущего сеанса
    - Приветствие пользователя
    - Побуждение к действию
    - Уведомление о некорректном ходе
    - Оповещение об окончании игры в зависимости от результата игрока
    
    Возвращает: 
    - Список информации, которую необходимо подать игроку"""

    # Статистика пользователя приводится к списку для удобной итерации по значениям
    ans = list(ANSWER_SPLIT)

    # К значениям побед и поражений присваивается статистика пользователя по ключам win и lost соответственно. 
    ans[1] += str(game_static[id_user]['win'])
    ans[2] += str(game_static[id_user]['lost'])

    # Считывание информации, которую нужно подать игроку  
    for i in range(len(strings)):
        ans.append(strings[i])
    
    # Возвращается список информации для подачи игроку с разделителем "новая строка". 
    return '\n'.join(ans)



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция отвечающая по запросу /help
    - Отвечает, что это крестики-нолики """

    await update.message.reply_text(f"{e(':christmas_tree:', language='alias')} Это крестики-нолики {e(':christmas_tree:', language='alias')}")



def great_field(number: list):
    """Функция заполнения поля

    Заполняет поле: 
    - Пустыми ячейками для нового пользователя или нового сеанса
    - Ячейками соответствующими статусу текущего поля, сохраненным за пользователем
    
    Возвращает поле (список списков) с соответствующе заполненными ячейками на основании прогресса пользователя"""
    
    return [[InlineKeyboardButton(text=TOKENEMP if number[i+j] in VALID else number[i+j], callback_data=str(i+j)) for i in range(3)] for j in [0, 3, 6]]



async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция старта игры"""

    # К переменной name присваивается информация о текущем пользователе
    name = update.message.from_user

    # logger сразу записывает информацию о том, что пользователь начал игру
    logger.info(f"User {name.first_name} started tic_tac_toe.")

    # Проверяется состояние текущего поля пользователя
    check_status(name.id)

    # Заводятся глобальные переменные smart_bot и first_move, чтобы ими можно было воспользоваться в других функциях
    global smart_bot

    global first_move

    # К данным переменным присваивается значение, которое возвращается из функции issmartbot() и first_move() соответственно
    smart_bot = issmartbot()

    first_move = first_move()

    # Заводятся 2 переменные - пустые строки, для вложения в них результата работы функций. 
    smart = ""

    move = ""

    # В зависимости от результата, выданного функцией на основании рандома, пустая строка будет изменена
    if first_move == True:
        move = f'Первый ход за тобой, {name.first_name} {e(":snowman:", language="alias")}'
    else:
        move = f'Первый ход за ботом! {e(":globe_with_meridians:", language="alias")}' 
    

    if smart_bot == True:
        smart = "Ты будешь играть с умным ботом!"
    else:
        smart = "Ты будешь играть с глупым ботом!"
    
    # Показывается табло с информацией для пользователя на основании его ID и аргумента strings. 
    answer = builde_answer(
        name.id, strings=[f'Привет {name.first_name}', move, smart, "Приятной игры!!!"])

    # Выводится табло с информацией, и само поле, которое выстраивается на основании информации,
    # полученной от id пользователя и статуса его текущего поля
    await update.message.reply_text(answer, reply_markup=InlineKeyboardMarkup(great_field(game_status[name.id])))
    


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция для взаимодействия с полем посредством callback-кнопок"""

    # Переменной query присваиваем значение нажатой кнопки
    query = update.callback_query

    # Клавиша нажата, ответ предоставляется в зависимости от условия
    await query.answer()

    # В случае, если пользователь попытался сходить на уже заполненную ячейку поля
    if query.data != game_status[query.from_user.id][int(query.data)]:

        # В ответ уходит информация для поступления на табло о том, что пользователь ходит неправильно
        # При условии такого хода - ничего не будет изменено, отправится лишь информация некорректного хода
        answer = builde_answer(query.from_user.id, strings=[
                              f'Хитришь {query.from_user.first_name}', 
                              'Играй честно \N{banana}'])

        # В любом случае, показываем клавиатуру для дальнейших шагов, заполняя ее соответственно состоянию поля пользователя                       
        await query.edit_message_text(answer, reply_markup=InlineKeyboardMarkup(great_field(game_status[query.from_user.id])))

    # В случае, если пользователь сходил правильно (на пустую ячейку поля)    
    else:

        # Ход переходит к боту, аргументом передаются уже нажатые кнопки
        result, answer = game_round(query)

        # Если бот сходил 5 раз
        if result == 5:

            # Игра прекращается, так как пустых ячеек больше нет, и выдается поле заполненное символами соперников            
            await query.edit_message_text(answer, reply_markup=InlineKeyboardMarkup(great_field(game_status[query.from_user.id])))

        # В случае, если еще остались пустые ячейки поля и обнаружилась победная комбинация   
        else:

            # Игра прекращается победой пользователя или бота, выдается поле заполненное символами соперников
            await query.edit_message_text(answer, reply_markup=InlineKeyboardMarkup(great_field(game_status[query.from_user.id])))

            # статус поля сбрасывается (создается новое пустое поле) 
            game_status[query.from_user.id] = list(FIELD_EMPTY).copy()

            # Создается запись об окончании игры в параметр "lastgame", указывающий на последнюю игру пользователя
            game_static[query.from_user.id]['lastgame'] = datetime.datetime.today().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            


def game_round(data):
    """Функция ходов по полю, определения победителя, присваивания статистики за результат"""
    
    # Ход пользователя меняет текущее состояние поля, на котором появляется символ пользователя
    game_status[data.from_user.id][int(data.data)] = TOKENPLAYER   

    # Происходит проверка на победную комбинацию символов пользователя 
    if checkwin(game_status[data.from_user.id], TOKENPLAYER):

        # В случае если результатом проверки вернется True, то к победам пользователя добавится 1 и запишется в статистику       
        game_static[data.from_user.id]['win'] += 1

        # В табло поступит информация о победе пользователя
        return 1, builde_answer(data.from_user.id, strings=[
            f'Ты победил {data.from_user.first_name}',
            'Молодец \N{VICTORY HAND}'])

    # В случае, если победная комбинация не обнаружена - произойдет проверка на "Ничью"
    elif check_draw (game_status[data.from_user.id]):

        # Если результатом проверки на ничью - вернется True то к победам и к поражениям добавится + 0.5 очков        
        game_static[data.from_user.id]['win'] += 0.5

        game_static[data.from_user.id]['lost'] += 0.5

        # В табло поступит информация о ничьей
        return 0, builde_answer(data.from_user.id, strings=[
            f"Победила дружба!!! {e(':couple:', language='alias')}"])

    # В случае, если ход пользователя не определяет ни победу, ни ничью        
    else:

        # Если переменная issmartbot на основании рандома имеет значение True (это глобальная переменная, полученная при старте)
        if smart_bot == True:

            # Происходит ход умного бота, анализирующего ситуацию и двигающегося по определенной стратегии для победы
            game_status[data.from_user.id][bot_ai(game_status[data.from_user.id])] = TOKENBOT
            
        # Если переменная issmartbot на основании рандома имеет значение False
        elif smart_bot == False:

            # Происходит ход глупого бота, действующего на основании рандома без определенной стратегии
            game_status[data.from_user.id][bot_move(game_status[data.from_user.id])] = TOKENBOT

        # Происходит проверка на победу бота        
        if checkwin(game_status[data.from_user.id], TOKENBOT):

            # В случае получения True в статистику пользователя добавляется + 1 к поражениям            
            game_static[data.from_user.id]['lost'] += 1

            # В табло поступает информация о поражении пользователя с утешением. 
            return -1, builde_answer(data.from_user.id, strings=[
                f'Ты проиграл {e(":worried:", language="alias")}', 
                f'Попробуй еще! У тебя обязательно получится {e(":sparkling_heart:", language="alias")}'])
                    
        # После хода в табло поступает информация о том, что теперь ход пользователя, с побуждением подумать.                           
    return 5, builde_answer(data.from_user.id, strings=[
        f'Подумайте хорошенько! {data.from_user.first_name}', f'Твой ход {e(":snowman:", language="alias")}'])



def bot_move(board:list):
    """Функция хода бота по принципу рандома (Глупый бот)"""

    # Используется флаг с булевым значением
    flag = True

    # До тех пор, пока флаг "поднят"
    while (flag):

        # Будет производиться рандом
        rand = rnd(0, 8)

        # В случае если ячейка не занята символом (так как по ходу игры числовые значения заменяются символами)
        if board[rand] == str(rand):

            # Возвращается значение рандома
            return rand



def bot_ai(board: list):
    """Функция хода бота по принципу minimax (Умный бот)"""

    # Используется лучший счет согласно правилу принятий решения mimimax
    best_score = -8

    # А так же лучший ход, которому изначально присваивается значения нуля
    best_move = 0

    # Происходит проверка всех ключей словаря board (числовых значений и символов)
    for key in range(len(board)):

        # В случае, если ключ - пустая ячейка (т.е. число, входящее в список валидных значений, а не символ)
        if board[key] in VALID:

            # Временной переменной temp присваивается этот ключ
            temp = board[key]

            # И бот ходит по данному ключу (в эту пустую ячейку)
            board[key] = TOKENBOT

            # Переменная score вызывает функцию minimax, анализирующую лучший возможный ход, который приведет к победе
            # Аргументами передает поле с только что сделанным ходом и значение False, определяющее принцип работы функции
            score = minimax(board, False)

            # Возвращает ключ в исходное состояние (убирает поставленный ранее символ) для проверки остальных вариантов
            board[key] = temp

            # В случае если score вернул значение большее, чем best_score (Тем самым выбирая лучший возможный ход)
            if score > best_score:

                # То лучшим счетом становится текущий счет
                best_score = score

                # А лучшим ходом будет являться тот ход, который является максимально стратегически выгодным
                best_move = key
    
    # Возвращаем результат лучшего возможного хода 
    return best_move



def minimax(board, is_maximizing):
    """Функция по принципу minimax. 
    - ### https://en.wikipedia.org/wiki/Minimax"""

    # Если вернулось значени True для бота - возвращаем 1, тем самым поощрая его за хороший ход
    if checkwin(board, TOKENBOT):
        return 1
    
    # Если вернулось значение True для пользователя - возвращаем -1, тем самым наказывая его за плохой ход
    elif checkwin(board, TOKENPLAYER):
        return -1
    
    # Если вернулась ничья - возвращаем 0, тем самым не поощрая, но и не наказывая бота за его ход. 
    # Применяется только в случае, если победная комбинация невозможна
    elif check_draw(board):
        return 0
    
    # В случае, если параметр is_maximizing, пришедший в функцию - True
    if is_maximizing:

        # Переменные настраиваются для максимизации возможности боту победить 
        best_score = -8
        token = TOKENBOT
        flag = False
    
    # В случае, если параметр is_maximizing, пришедший в функцию - False
    else:

        # Переменные настраиваются для минимизации возможности пользователю победить 
        best_score = 8
        token = TOKENPLAYER
        flag = True

    # Происходит проверка всех ключей словаря board (числовых значений и символов)    
    for key in range(len(board)):

        # В случае, если ключ - пустая ячейка (т.е. число, входящее в список валидных значений, а не символ)
        if board[key] in VALID:

            # Временной переменной temp присваивается этот ключ
            temp = board[key]

            # Символ бота или пользователя ставится в эту пустую ячейку
            board[key] = token

            # Переменная score вызывает функцию рекурсивно для проверки лучших ходов как бота, так и пользователя
            # Аргументами передает поле с только что сделанным ходом и булево значение, определяющее принцип работы функции
            score = minimax(board, flag)

            # Возвращает ключ в исходное состояние (убирает поставленный ранее символ) для проверки остальных вариантов
            board[key] = temp

            # В зависимости от булева значения определяется принцип оценки лучшего хода для бота.
            # В случае, если значение флага - True
            if flag:

                # Выполняется минимизация шанса на победу пользователя 
                if score < best_score:

                    # И лучшему счету (худшему, с точки зрения пользователя) присваивается score
                    best_score = score
            # В случае, если значение флага - False
            else:

                # Выполняется максимизация шанса на победу бота
                if score > best_score:

                    # И лучшему счету (с точки зрения бота) присваивается score
                    best_score = score

    # Возвращается значение лучшего счета для передачи AI. 
    # Тем самым у него появляется стратегия правильных ходов для достижения победы или ничьи.
    # На основании этих данных он не может проиграть ни в каком случае, куда бы пользователь не сходил.      
    return best_score



def check_draw(board):
    """Функция проверки на ничью
    
    Возвращает булево значение:

    - False, в случае, если еще остались пустые ячейки
    - True, если нет"""

    # Происходит проверка всех ключей словаря board
    for key in range(len(board)):

        # В случае если ключ валиден (если это пустая ячейка, а не символ)
        if board[key] in VALID:

            # Возвращается значение False
            return False

    # В случае, если пустых ячеек не обнаружилось - возвращается True
    return True



def checkwin(board: list, mark: str):
    """Функция проверки на победу
    
    Возвращает булево значение:

    - True, В случае, если комбинация символов имеется в списке победных комбинаций
    - False, В случае, если текущая комбинация не победная"""

    # Происходит проверка комбинаций из списка WINS_LINE, в котором хранятся все победные комбинации
    for each in WINS_LINE:

        # Если комбинации символов имеется в списке победных комбинаций
        if board[each[0]] == board[each[1]] == board[each[2]] == mark:

            # Возвращается True
            return True

    # В случае, если поставленный символ не создает победную комбинацию, возвращается False
    return False



def issmartbot():
    """На основании рандома определяется то, как именно будет ходить бот
    - Если возвращается False - бот будет ходить рандомно, невзирая на стратегию
    - Если возвращается True - бот будет ходить на основании анализа поведения пользователя и лучшего возможного хода
    с точки зрения стратегии для неминуемой победы над пользователем. Такой бот не способен проиграть."""

    # Переменная toss (бросок) определяет рандомное число от 0 до 100
    toss_smart = rnd(0, 101)

    print(f'Бот = {toss_smart}') # для проверки того, какой бот будет включен в терминале

    # Возвращается булево значение соответствующее рандомному значению (шансы 50 на 50 для каждого из вариантов бота)
    return False if toss_smart > 50 else True



def first_move():
    """На основании рандома определяется то, кто будет ходить первым
    - Если возвращается False - бот будет ходить первым
    - Если возвращается True - пользователь будет ходить первым """

    # Переменная toss (бросок) определяет рандомное число от 0 до 100
    toss_move = rnd(0, 101)

    print(f'Первый ход = {toss_move}') # для проверки того, кто будет ходить первым в терминале

    # Возвращается булево значение соответствующее рандомному значению (шансы 50 на 50 для бота и для пользователя)
    return False if toss_move > 50 else True



if __name__ == '__main__':
    app = ApplicationBuilder().token(mytoken.MYTOKEN).build()
    app.add_handler(CommandHandler('start', start_game))    
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CallbackQueryHandler(buttons))
    app.run_polling()
    save_static(game_static)