# Игра: "Джеймс Джойс или компьютер?"
#
# Веб-сервис, который играет с пользователем в игру:
#   предлагает угадать, оригинальное ли перед ним предложение
#   какого-либо автора или сгенерированное компьютером с помощью
#   word2vec. В конце показывает результат пользователя и статистику
#   правильных ответов.

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
    return render_template('index.html')


@app.route('/rules')
def rules():
    return render_template('rules.html')


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
    return render_template('stat.html')


if __name__ == '__main__':
    app.run(debug=True)
