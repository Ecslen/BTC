import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
)
import sqlite3
from datetime import datetime

# Ведение журнала логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
print(logging.INFO)
logger = logging.getLogger(__name__)

# Этапы/состояния разговора
FIRST, SECOND = range(2)
# Данные обратного вызова

PROFILE, WALLET, MY_VIDEO_CARDS, BACK, SHOP, CONVERT, ONE_V, TWO_V, THREE_V, FOUR_V, FIVE_V, SIX_V, SEVEN_V, \
EIGHT_V, NINE_V, TEN_V, CUCCES = range(17)

gpus = ["MSI GeForce GTX 1050 TI", "Palit GeForce GTX 1060",
        "Nvidia GeForce GTX 1650", "Inno3D GeForce GTX 1660",
        "Asus GeForce GTX 1070", "Gigabyte GeForce GTX 1080",
        "Asus GeForce GTX 1080 TI", "Palit GeForce GTX 2060",
        "MSI GeForce GTX 2070", "Nvidia GeForce GTX 2080"]

GPU_earning = {
    "MSI GeForce GTX 1050 TI": 0.5, "Palit GeForce GTX 1060": 0.7,
    "Nvidia GeForce GTX 1650": 0.8, "Inno3D GeForce GTX 1660": 0.85,
    "Asus GeForce GTX 1070": 0.9, "Gigabyte GeForce GTX 1080": 0.95,
    "Asus GeForce GTX 1080 TI": 0.97, "Palit GeForce GTX 2060": 0.99,
    "MSI GeForce GTX 2070": 1.1, "Nvidia GeForce GTX 2080": 1.6

}

gpu_cost = {
    "MSI GeForce GTX 1050 TI": 3000, "Palit GeForce GTX 1060": 4500,
    "Nvidia GeForce GTX 1650": 6500, "Inno3D GeForce GTX 1660": 7000,
    "Asus GeForce GTX 1070": 8550, "Gigabyte GeForce GTX 1080": 9900,
    "Asus GeForce GTX 1080 TI": 12000, "Palit GeForce GTX 2060": 15590,
    "MSI GeForce GTX 2070": 18900, "Nvidia GeForce GTX 2080": 20000,
}


balance = 0  # Берем баланс из бд(всегда в функциях)
videocards = 'Их нет'  # Берем баланс


def myVideva(idU):
    global videocards
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    videocards = cur.execute("""SELECT cards FROM game WHERE id = ?""", [idU])


def start(update, _):
    """Вызывается по команде `/start`."""
    # Получаем пользователя, который запустил команду `/start`
    user = update.message.from_user
    logger.info("Пользователь %s начал разговор", user.first_name)

    # получаем id пользователя
    user_check(user.id)
    # Создаем `InlineKeyboard`, где каждая кнопка имеет
    # отображаемый текст и строку `callback_data`
    # Клавиатура - это список строк кнопок, где каждая строка,
    # в свою очередь, является списком `[[...]]`
    keyboard = [
        [
            InlineKeyboardButton("Профиль", callback_data=str(PROFILE)),
            InlineKeyboardButton("Кошелек", callback_data=str(WALLET))
        ],
        [
            InlineKeyboardButton("Магазин видеокарт", callback_data=str(SHOP))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Добро пожаловать в ферму BTC! Ждем действий!')
    # Отправляем сообщение с текстом и добавленной клавиатурой `reply_markup`
    update.message.reply_text(
        text=f"Твой баланс: {loadMoney(user.id)}", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас состояние `FIRST`
    return FIRST


def start_over(update, _):
    """Тот же текст и клавиатура, что и при `/start`, но не как новое сообщение"""
    # Получаем `CallbackQuery` из обновления `update`
    query = update.callback_query
    # На запросы обратного вызова необходимо ответить,
    # даже если уведомление для пользователя не требуется.
    # В противном случае у некоторых клиентов могут возникнуть проблемы.
    now_user = query['message']['chat']['id']
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Профиль", callback_data=str(PROFILE)),
            InlineKeyboardButton("Кошелек", callback_data=str(WALLET)),
        ],
        [
            InlineKeyboardButton("Магазин видеокарт", callback_data=str(SHOP))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Отредактируем сообщение, вызвавшее обратный вызов.
    # Это создает ощущение интерактивного меню.
    query.edit_message_text(
        text=f"Твой баланс: {loadMoney(now_user)}", reply_markup=reply_markup
    )
    # Сообщаем `ConversationHandler`, что сейчас находимся в состоянии `FIRST`
    return FIRST


def prof(update, _):
    """Показ нового выбора кнопок"""
    query = update.callback_query

    now_user = query['message']['chat']['id']

    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Назад", callback_data=str(BACK)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"""Профиль: 
Ник: {query['message']['chat']['username']}
Мощность видеокарт: 
                    """, reply_markup=reply_markup
    )
    return FIRST


def wallet(update, _):
    """Показ нового выбора кнопок"""
    query = update.callback_query

    now_user = query['message']['chat']['id']
    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Назад", callback_data=str(BACK)),
            InlineKeyboardButton("Конвертировать", callback_data=str(CONVERT)),

        ],
    ]
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    lastM = cur.execute("""SELECT btc FROM game WHERE playerId = ?""", [now_user])
    for i in lastM:
        lastM = int(i[0])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"У вас есть {lastM} битков", reply_markup=reply_markup
    )
    CheckMiningMoney(now_user)
    return FIRST


def shop(update, _):
    """Показ выбора кнопок"""
    query = update.callback_query

    now_user = query['message']['chat']['id']

    query.answer()
    keyboard = [
        [
            InlineKeyboardButton("MSI GeForce GTX 1050 TI", callback_data=str(ONE_V)),
        ],
        [
            InlineKeyboardButton("Palit GeForce GTX 1060", callback_data=str(TWO_V)),
        ],
        [
            InlineKeyboardButton("Nvidia GeForce GTX 1650", callback_data=str(THREE_V)),
        ],
        [
            InlineKeyboardButton("Inno3D GeForce GTX 1660", callback_data=str(FOUR_V)),
        ],
        [
            InlineKeyboardButton("Asus GeForce GTX 1070", callback_data=str(FIVE_V)),
        ],
        [
            InlineKeyboardButton("Gigabyte GeForce GTX 1080", callback_data=str(SIX_V)),
        ],
        [
            InlineKeyboardButton("Asus GeForce GTX 1080 TI", callback_data=str(SEVEN_V)),
        ],
        [
            InlineKeyboardButton("Palit GeForce GTX 2060", callback_data=str(EIGHT_V)),
        ],
        [
            InlineKeyboardButton("MSI GeForce GTX 2070", callback_data=str(NINE_V)),
        ],
        [
            InlineKeyboardButton("Nvidia GeForce GTX 2080", callback_data=str(TEN_V)),
        ],
        [
            InlineKeyboardButton("Назад", callback_data=str(BACK)),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text="""Магазин видеокарт:
    MSI GeForce GTX 1050 TI: 3000, 
    Palit GeForce GTX 1060: 4500,
    Nvidia GeForce GTX 1650: 6500, 
    Inno3D GeForce GTX 1660: 7000,
    Asus GeForce GTX 1070: 8550, 
    Gigabyte GeForce GTX 1080: 9900,
    Asus GeForce GTX 1080 TI: 12000, 
    Palit GeForce GTX 2060: 15590,
    MSI GeForce GTX 2070: 18900, 
    Nvidia GeForce GTX 2080: 20000,""", reply_markup=reply_markup
    )
    return FIRST


# Для конвертации в деньги функция
def convertor(update, _):
    """Показ выбора кнопок"""
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    keyboard = [
        [
            InlineKeyboardButton("Конвертировать", callback_data=str(CUCCES)),
            InlineKeyboardButton("Назад", callback_data=str(BACK)),
        ]
    ]
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    lastM = cur.execute("""SELECT btc FROM game WHERE playerId = ?""", [now_user])
    for i in lastM:
        lastM = int(i[0])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        text=f"Вы можете конвертировать свои btc в баланс. У вас сейчас {lastM} btc", reply_markup=reply_markup
    )
    return FIRST


def success_convert(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    lastM = cur.execute("""SELECT btc FROM game WHERE playerId = ?""", [now_user])
    for i in lastM:
        lastM = int(i[0])
    keyboard = [
        [
            InlineKeyboardButton("Назад", callback_data=str(BACK)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    lBalance = cur.execute("""SELECT balance FROM game WHERE playerId = ?""", [now_user])
    for i in lBalance:
        lBalance = int(i[0])
    cur.execute("""UPDATE game SET (balance) = (?) WHERE playerId = ?""", (lBalance + lastM * 500, now_user))
    cur.execute("""UPDATE game SET (btc) = (?) WHERE playerId = ?""", (0, now_user))
    con.commit()
    query.edit_message_text(
        text=f"Вы успешно конвертировали свои btc в баланс. У вас сейчас 0 btc",
        reply_markup=reply_markup
    )
    return FIRST


# отвечает за покупку видюхи
def buy_01(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[0]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )

        addCards(now_user, GPU_earning[gpus[0]], 3000)  # now_user, имя видюхиб скок фармитTT
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


def buy_02(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[1]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )
        # тут добавление этой видюхи в бд
        addCards(now_user, GPU_earning[gpus[1]], 4500)
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


def buy_03(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[2]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )
        # тут добавление этой видюхи в бд
        addCards(now_user, GPU_earning[gpus[2]], 6500)
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


def buy_04(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[3]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )
        # тут добавление этой видюхи в бд
        addCards(now_user, GPU_earning[gpus[3]], 7000)
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


# отвечает за покупку видюхи
def buy_05(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[4]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )
        # тут добавление этой видюхи в бд
        addCards(now_user, GPU_earning[gpus[4]], 8550)
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


# отвечает за покупку видюхи
def buy_06(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[5]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )
        # тут добавление этой видюхи в бд
        addCards(now_user, GPU_earning[gpus[5]], 9900)
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


# отвечает за покупку видюхи
def buy_07(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[6]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )
        # тут добавление этой видюхи в бд
        addCards(now_user, GPU_earning[gpus[6]], 12000)
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


# отвечает за покупку видюхи
def buy_08(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[7]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )
        # тут добавление этой видюхи в бд
        addCards(now_user, GPU_earning[gpus[7]], 15990)
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


# отвечает за покупку видюхи
def buy_09(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[8]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )
        # тут добавление этой видюхи в бд
        addCards(now_user, GPU_earning[gpus[8]], 18900)
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


# отвечает за покупку видюхи
def buy_10(update, _):
    query = update.callback_query
    query.answer()
    now_user = query['message']['chat']['id']
    if loadMoney(now_user) >= gpu_cost[gpus[9]]:
        """Показ нового выбора кнопок"""
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вы приобрели данную видеокарту", reply_markup=reply_markup
        )
        # тут добавление этой видюхи в бд
        addCards(now_user, GPU_earning[gpus[9]], 20000)
        return FIRST
    else:
        keyboard = [
            [
                InlineKeyboardButton("Назад", callback_data=str(BACK)),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Вам не хватает кеша", reply_markup=reply_markup
        )


def user_check(idU):
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    curnUser = cur.execute("""SELECT playerId FROM game""")
    check = False
    for i in curnUser:
        if idU == i[0]:
            check = True
    if not check:
        start_bal = 3000
        new_time = datetime.now()  # Новое время при повторном заходе
        cur.execute("""INSERT INTO game (playerId, balance, power, btc, lasttime) VALUES (?, ?, ?, ?, ?)""",
                    (idU, start_bal, 0, 0, new_time))
        con.commit()


def loadBtc(idU):
    pass


# idU - айди пользователя получаемое в now_user = query['message']['chat']['id']
def loadMoney(idU):
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    curnMoney = cur.execute("""SELECT balance FROM game WHERE playerId = ?""", [idU])
    for i in curnMoney:
        return i[0]


# мои видюхи
def MyCards(idU):
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    curnCards = cur.execute("""SELECT cards FROM game WHERE id = ?""", [idU])


# добавление новой видюхи
def addCards(idU, powerCard, costCard):
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    curnPower = cur.execute("""SELECT power FROM game WHERE playerId = ?""", [idU])
    for i in curnPower:
        curnPower = i[0]
    powers = curnPower + powerCard
    curnBALANCE = cur.execute("""SELECT balance FROM game WHERE playerId = ?""", [idU])
    for i in curnBALANCE:
        bal = i[0]
        bal -= costCard

    new_time = datetime.now().date()
    cur.execute("""UPDATE game SET (power) = (?) WHERE playerId = ?""", (powers, idU))
    cur.execute("""UPDATE game SET (balance) = (?) WHERE playerId = ?""", (bal, idU))
    cur.execute("""UPDATE game SET (lasttime) = (?) WHERE playerId = ?""", (new_time, idU))
    con.commit()


def CheckMiningMoney(idU):
    con = sqlite3.connect('base.db')
    cur = con.cursor()
    lasttime = cur.execute("""SELECT lasttime FROM game WHERE playerId = ?""", [idU])
    for i in lasttime:
        lasttimee = str(i[0])
    pp = cur.execute("""SELECT power FROM game WHERE playerId = ?""", [idU])
    for i in pp:
        pp = i[0]
    days = lasttimee.split('-')
    NEWTIME = str(datetime.now().date()).split('-')
    print(NEWTIME[0], days[0])
    year = int(NEWTIME[0]) - int(days[0])
    month = int(NEWTIME[1]) - int(days[1])
    day = int(NEWTIME[2]) - int(days[2])
    lastM = cur.execute("""SELECT btc FROM game WHERE playerId = ?""", [idU])
    for i in lastM:
        lastM = int(i[0])
    Money = pp * 360 * year + pp * 31 * month + day * pp + 2
    Money += lastM
    print(Money)
    cur.execute("""UPDATE game SET (btc) = (?) WHERE playerId = ?""", (Money, idU))
    con.commit()


def end(update, _):
    """Возвращает `ConversationHandler.END`, который говорит
    `ConversationHandler` что разговор окончен"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


TOKEN = '1604427826:AAH-oyzCfKqlafDG_xJLzazmxbtGoh-CzXA'
if __name__ == '__main__':
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Настройка обработчика разговоров с состояниями `FIRST` и `SECOND`
    # Используем параметр `pattern` для передачи `CallbackQueries` с
    # определенным шаблоном данных соответствующим обработчикам
    # ^ - означает "начало строки"
    # $ - означает "конец строки"
    # Таким образом, паттерн `^ABC$` будет ловить только 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={  # словарь состояний разговора, возвращаемых callback функциями
            FIRST: [
                CallbackQueryHandler(prof, pattern='^' + str(PROFILE) + '$'),
                CallbackQueryHandler(wallet, pattern='^' + str(WALLET) + '$'),
                CallbackQueryHandler(start_over, pattern='^' + str(BACK) + '$'),
                CallbackQueryHandler(shop, pattern='^' + str(SHOP) + '$'),
                CallbackQueryHandler(buy_01, pattern='^' + str(ONE_V) + '$'),
                CallbackQueryHandler(buy_02, pattern='^' + str(TWO_V) + '$'),
                CallbackQueryHandler(buy_03, pattern='^' + str(THREE_V) + '$'),
                CallbackQueryHandler(buy_04, pattern='^' + str(FOUR_V) + '$'),
                CallbackQueryHandler(buy_05, pattern='^' + str(FIVE_V) + '$'),
                CallbackQueryHandler(buy_06, pattern='^' + str(SIX_V) + '$'),
                CallbackQueryHandler(buy_07, pattern='^' + str(SEVEN_V) + '$'),
                CallbackQueryHandler(buy_08, pattern='^' + str(EIGHT_V) + '$'),
                CallbackQueryHandler(buy_09, pattern='^' + str(NINE_V) + '$'),
                CallbackQueryHandler(buy_10, pattern='^' + str(TEN_V) + '$'),
                CallbackQueryHandler(convertor, pattern='^' + str(CONVERT) + '$'),
                CallbackQueryHandler(success_convert, pattern='^' + str(CUCCES) + '$'),

            ],
            SECOND: [
                CallbackQueryHandler(start_over, pattern='^' + str(PROFILE) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(WALLET) + '$'),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    # Добавляем `ConversationHandler` в диспетчер, который
    # будет использоваться для обработки обновлений
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
