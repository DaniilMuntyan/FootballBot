import telebot
from urllib.request import urlopen
from bs4 import BeautifulSoup

token = "935353360:AAE83gmB71BehP3mB9t6hGZEb-619WpKiTA"

bot = telebot.TeleBot(token)

begin = 0

def getList():
    url = 'https://terrikon.com/football/ukraine/championship/table'
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    list_ = dict()
    for data in soup.findAll('tr'):
        if len(data.text.split('\n')) != 14:
            continue
        for ref in data.findAll('a', href=True, title=False):
            site = ref.get('href').split('/')
            list_[data.text.split('\n')[2].strip().lower()] = site[len(site) - 1]
    return list_

@bot.message_handler(commands=['start', 'help'])
def command_help(message):
    if message.text == '/help':
        bot.reply_to(message, "Вот что я могу:\n" +
                 "\"Список\" - все команды, участвующие в текущем сезоне\n" +
                 "\"Сезоны\" - ссылки на все сезоны Чемпионата\n" +
                 "\"Фк *название клуба*\" - статистика футбольного клуба в текущем сезоне Чемпионата Украины\n" +
                 "\"Матчи *название клуба*\" - состоявшиеся и будущие футбольные встречи клуба в рамках текущего " +
                 "сезона\n" +
                 "\"Бомбардиры\" - топ 10 лучших игроков сезона\n" +
                 "\"Состав *название клуба*\" - данные игроков команды\n\n" +
                 "Команды к регистру не чувствительны. Все данные актуальны (terrikon.com) и регулярно обновляются")
    else:
        global begin
        begin = 1
        bot.reply_to(message, "Вы можете ввести такие команды:\n" +
                     "\"Список\"\n" +
                     "\"Сезоны\"\n" +
                     "\"Фк *название клуба*\"\n" +
                     "\"Матчи *название клуба*\"\n" +
                     "\"Бомбардиры\"\n" +
                     "\"Состав *название клуба*\"\n\n" +
                     "Все данные актуальны и регулярно обновляются")

@bot.message_handler(content_types=["text"])
def handle_message(message):
    if begin == 0:
        bot.send_message(message.chat.id, "Сначала запустите бота (/start)")
        return
    try:
        if message.text.strip().lower() == 'список':
            s = ""
            i = 1
            for temp in getList():
                s += str(i) + ". " + temp.title() + "\n"
                i += 1
            bot.reply_to(message, s)
        elif "фк " in message.text.strip().lower():
            text = message.text.strip().lower().split(' ')
            if len(text) != 2:
                bot.reply_to(message, "Введите команду правильно")
                return
            url = 'https://terrikon.com/football/ukraine/championship/table'
            html = urlopen(url).read()
            soup = BeautifulSoup(html, "html.parser")
            for data in soup.findAll('tr'):
                if data.text.split('\n')[2].strip().lower() == text[1]:
                    games = int(data.text.split('\n')[5].strip())
                    wins = int(data.text.split('\n')[6].strip())
                    draw = int(data.text.split('\n')[7].strip())
                    losing = int(data.text.split('\n')[8].strip())
                    scored = int(data.text.split('\n')[9].strip())
                    missed = int(data.text.split('\n')[11].strip())
                    points = int(data.text.split('\n')[12].strip())
                    bot.reply_to(message, "Игр: " + str(games) + '\n' +
                                 "Выиграно: " + str(wins) + '\n' +
                                 "Вничью: " + str(draw) + '\n' +
                                 "Проиграно: " + str(losing) + '\n' +
                                 "Забитые голы: " + str(scored) + '\n' +
                                 "Пропущенные голы: " + str(missed) + '\n' +
                                 "Очки: " + str(points))
                    return
            bot.reply_to(message, "Ошибка запроса")
        elif "матчи " in message.text.strip().lower():
            text = message.text.strip().lower().split(' ')
            if len(text) != 2:
                bot.reply_to(message, "Введите команду правильно")
                return
            url = 'https://terrikon.com/football/ukraine/championship/table'
            html = urlopen(url).read()
            soup = BeautifulSoup(html, "html.parser")
            for data in soup.findAll('tr'):
                if data.text.split('\n')[2].strip().lower() == text[1]:
                    t = ""
                    t = t.upper()
                    for ref in data.findAll('a', href=True, title=True):
                        t += f'[{ref.get("title")}]({"https://terrikon.com" + ref.get("href")})' + "\n"
                    bot.reply_to(message, t, parse_mode='Markdown')
                    break
        elif message.text.strip().lower() == "бомбардиры":
            url = 'https://terrikon.com/football/ukraine/championship/strikers'
            html = urlopen(url).read()
            soup = BeautifulSoup(html, "html.parser")
            list = []
            answer = ("ТОП 10:\n\n")
            list.append(answer)
            count = 0
            for data in soup.findAll('tr'):
                if count == 0:
                    count += 1
                    continue
                count += 1
                t = (data.text.split('\n')[1] + ' ' + data.text.split('\n')[2] + " (" + data.text.split('\n')[3].strip() +
                     ")" + '\n' + "Забитых мячей: " + data.text.split('\n')[4] + '\n' + "Игр сыграно: " +
                     data.text.split('\n')[6] + '\n' + 'В среднем голов за игру: ' + data.text.split('\n')[7] + '\n\n')
                list.append(t)
                if count > 10:
                    break
            bot.reply_to(message, "".join(list))
        elif "состав " in message.text.strip().lower():
            list_ = getList()
            text = message.text.strip().lower().split(' ')
            if len(text) != 2:
                bot.reply_to(message, "Введите команду правильно")
                return
            url = 'https://terrikon.com/football/teams/' + str(list_[text[1].strip()]) + '/players'
            html = urlopen(url).read()
            soup = BeautifulSoup(html, "html.parser")
            answer = [""]
            c = 0
            for data in soup.findAll('tr'):
                if len(data.text.split('\n')) == 9:
                    t = data.text.split('\n')[3] + ", " +  data.text.lower().split('\n')[4] + "\nФутбольный номер: " + \
                        data.text.split('\n')[1] + "\nДата рождения: " + data.text.split('\n')[5] +\
                        "\nРост: " + data.text.split('\n')[6] + "\nВес: " + data.text.split('\n')[7] + "\n"
                    if data.find('a', href=True):
                        for ref in data.findAll('a', href=True):
                            t += "Сайт игрока: " + "https://terrikon.com" + ref.get('href') + " \n\n"
                    answer.append(t)
                    c += len(t)
            if c > 4096:
                bot.reply_to(message, "".join(answer[0:int(len(answer) / 2)]), disable_web_page_preview=True)
                bot.send_message(message.chat.id, "".join(answer[int(len(answer) / 2):]), disable_web_page_preview=True)
            else:
                bot.reply_to(message, "".join(answer), disable_web_page_preview=True)
        elif message.text.strip().lower() == "сезоны":
            url = 'https://terrikon.com/football/ukraine/championship/table'
            html = urlopen(url).read()
            soup = BeautifulSoup(html, "html.parser")
            s = ""
            for data in soup.findAll('dd'):
                if data.text.strip().lower().endswith("чемпионат украины"):
                    for temp in data.findAll('a', href=True):
                        s += f'[{temp.text}]({"https://terrikon.com" + temp.get("href")})' + "\n"
            bot.reply_to(message, s, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            bot.reply_to(message, "Такой запрос не обрабатывается")
    except Exception:
        bot.reply_to(message, "Ошибка запроса")


bot.polling()
