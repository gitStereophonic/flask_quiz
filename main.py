# Игра: "Джеймс Джойс или компьютер?"
#
# Веб-сервис, который играет с пользователем в игру:
#   предлагает угадать, оригинальное ли перед ним предложение
#   какого-либо автора или сгенерированное компьютером с помощью
#   word2vec. В конце показывает результат пользователя и статистику
#   правильных ответов.

import gensim
import os
import urllib

import getpost

from flask import Flask
from flask import redirect, url_for, render_template, request
from pymystem3 import Mystem

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

model = None
quotes = []

m = 'ruscorpora_mystem_cbow_300_2_2015.bin.gz'
q = 'static/quotes'
db = 'users.db'

currentUser = {}


getpost.dowload_model(m)                # загружаем модель
quotes = getpost.download_quotes(q)     # загружаем цитаты
getpost.create_database(db)             # создаем базу данных

if m.endswith('.vec.gz'):
    model = gensim.models.KeyedVectors.load_word2vec_format(
        'static/' + m, binary=False)
elif m.endswith('.bin.gz'):
    model = gensim.models.KeyedVectors.load_word2vec_format(
        'static/' + m, binary=True)
else:
    model = gensim.models.KeyedVectors.load(m)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/rules')
def rules():
    return render_template('rules.html')


@app.route('/quiz')
def quiz():
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

    print(currentUser)
    getpost.save_to_database(currentUser, db)
    return render_template('quiz.html')


@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/stat')
def stat():
    return render_template('stat.html')


if __name__ == '__main__':
    app.run(debug=True)
