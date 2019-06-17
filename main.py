# Игра: "Джеймс Джойс или компьютер?"
#
# Веб-сервис, который играет с пользователем в игру:
#   предлагает угадать, оригинальное ли перед ним предложение
#   какого-либо автора или сгенерированное компьютером с помощью
#   word2vec. В конце показывает результат пользователя и статистику
#   правильных ответов.

from threading import Thread
import os
import random
import urllib

import getpost
import lingwork

from flask import Flask
from flask import redirect, url_for, render_template, request

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

model = None
quotes = []

q = 'static/quotes'
db = 'users.db'

currentUser = {}
finalQuotes = []
qCount = 15
qGenerated = 0
qOriginal = 0


quotes = getpost.download_quotes(q)     # загружаем цитаты
getpost.create_database(db)             # создаем базу данных


@app.route('/')
def index():
    t1 = Thread(target=lingwork.get_model)
    t1.start()
    return render_template('index.html')


@app.route('/rules')
def rules():
    return render_template('rules.html', qCount=qCount)


@app.route('/quiz')
def quiz():
    global qGenerated
    global qOriginal
    # получаем данные, которые пользователь указал о себе
    currentUser['userName'] = request.args['userName']
    currentUser['userGen'] = request.args['userGen']
    currentUser['userAge'] = request.args['userAge']
    currentUser['userCor'] = 0
    currentUser['userIncor'] = 0
    if request.args['userCity']:
        currentUser['userCity'] = request.args['userCity']
    else:
        currentUser['userCity'] = ''
    if request.args['userEdu']:
        currentUser['userEdu'] = request.args['userEdu']
    else:
        currentUser['userEdu'] = ''

    # подбор и генерация цитат
    finalQuotes.clear()
    rands = random.sample(range(len(quotes)), qCount)
    selection = []
    for r in rands:
        selection.append(quotes[r])

    qGenerated = random.randint(qCount / 3, qCount * 2 / 3)
    rands = random.sample(range(qCount), qGenerated)
    index = 0
    for sel in selection:
        splited = lingwork.split_book(sel)
        splited['key'] = 'quote_' + str(index)
        finalQuotes.append(splited)
        index += 1

    for randed in rands:
        finalQuotes[randed] = lingwork.change_quote(finalQuotes[randed])
    qOriginal = qCount - qGenerated

    return render_template('quiz.html', genCount=qGenerated, origCount=qOriginal,
                           quotes=finalQuotes)


@app.route('/result')
def result():
    wrongAn = 0
    correctAn = 0
    for q in finalQuotes:
        if q['key'] in request.args:
            origAn = request.args[q['key']] == 'original'
            if q['original'] == origAn:
                correctAn += 1
            else:
                wrongAn += 1

    currentUser['userCor'] = correctAn
    currentUser['userIncor'] = wrongAn
    getpost.save_to_database(currentUser, db)
    return render_template('result.html', wrongAn=wrongAn, correctAn=correctAn,
                           genCount=qGenerated, origCount=qOriginal)


@app.route('/stat')
def stat():
    data = getpost.get_data(db)
    allUsers = len(data)
    allCorr = 0
    allWron = 0
    coolUsers = 0
    agePc = 0
    ages = {'Меньше 18': 0, '18-25': 0, '26-40': 0, '41-60': 0, 'Больше 60': 0}

    for user in data:
        ages[user['age']] += 1
        allCorr += user['correct']
        allWron += user['wrong']

        questions = user['correct'] + user['wrong']
        if round((user['correct'] * 100.0) / questions, 1) > 50:
            coolUsers += 1

    print('ages:', ages)
    list_d = list(ages.items())
    list_d.sort(key=lambda i: i[1], reverse=True)
    agePc = list_d[0][0]

    allAn = allCorr + allWron
    pcCorr = round((allCorr * 100.0) / allAn, 1)
    pcWron = round((allWron * 100.0) / allAn, 1)

    return render_template('stat.html', allUsers=allUsers, allCorr=allCorr,
                           allWron=allWron, pcCorr=pcCorr, pcWron=pcWron,
                           coolUsers=coolUsers, agePc=agePc)


if __name__ == '__main__':
    app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
