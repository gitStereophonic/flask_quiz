import progressbar
import urllib
import sqlite3
import os

table = 'users'
db_folder = 'db/'
pbar = None


# вспомогательная функция для отслеживания состояния скачивания
def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None


# функция для скачивания модели с сайта rusvectores
def dowload_model(name):
    if not os.path.exists('static/' + name):
        if not os.path.exists('static/'):
            os.mkdir('static')

        print('Downloading...')
        urllib.request.urlretrieve(
            "http://rusvectores.org/static/models"
            "/rusvectores2/" + name,
            'static/' + name, show_progress)
        print('Download Completed!')


# функция для загрузки исходных данных
def download_quotes(file):
    if not os.path.exists(file):
        return []

    with open(file, 'r') as f:
        quotes = [line.rstrip('\n') for line in f]

    return quotes


# создание новой базы данных, если ее нет
def create_database(db_name=''):
    db_path = db_folder + db_name
    if not os.path.exists(db_path):
        if not os.path.exists(db_folder):
            os.mkdir(db_folder)

        connection = sqlite3.connect(db_path)
        c = connection.cursor()

        c.execute("DROP TABLE IF EXISTS " + table)
        c.execute("CREATE TABLE IF NOT EXISTS " + table + " (name STRING, "
                  "city STRING, edu STRING, gen STRING, "
                  "age STRING, corrects INTEGER, incorrects INTEGER)")

        connection.commit()
        connection.close()


# сохранение результатов пользователя в базу данных
def save_to_database(user, db_name=''):
    connection = sqlite3.connect(db_folder + db_name)
    c = connection.cursor()

    c.execute(
        "INSERT INTO " + table + " VALUES (?,?,?,?,?,?,?)",
        (user['userName'], user['userCity'],
         user['userEdu'], user['userGen'], user['userAge'],
         user['userCor'], user['userIncor'])
    )

    connection.commit()
    connection.close()


# загрузка всех данных из базы данных для статистических подсчетов
def get_data(db_name=''):
    result = []
    connection = sqlite3.connect(db_folder + db_name)
    c = connection.cursor()

    words = []
    for row in c.execute("SELECT * FROM " + table):
        name = row[0]
        city = row[1]
        edu = row[2]
        gen = row[3]
        age = row[4]
        cor = row[5]
        wrn = row[6]
        result.append({
            'name': name,
            'city': city,
            'edu': edu,
            'gen': gen,
            'age': age,
            'correct': cor,
            'wrong': wrn
        })

    return result
