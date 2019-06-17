import getpost

import gensim
import random
import re

from pymorphy2 import MorphAnalyzer

morph = MorphAnalyzer()

m = 'ruscorpora_mystem_cbow_300_2_2015.bin.gz'
getpost.dowload_model(m)  # загружаем модель

if m.endswith('.vec.gz'):
    model = gensim.models.KeyedVectors.load_word2vec_format(
        'static/' + m, binary=False)
elif m.endswith('.bin.gz'):
    model = gensim.models.KeyedVectors.load_word2vec_format(
        'static/' + m, binary=True)
else:
    model = gensim.models.KeyedVectors.load(m)


def split_book(phrase):
    p = re.compile(r'\("(.*?)"\)')
    book = re.findall(r'\("(.*?)"\)', phrase)[0]
    phrase = p.sub('', phrase)
    result = {'key': '', 'book': book, 'phrase': phrase, 'original': True}
    return result


def change_quote(smart_quote):
    phrase = smart_quote['phrase']

    for a in phrase.split(' '):
        isUpper = False
        if len(a) > 0:
            isUpper = a[0].isupper()
        ana = morph.parse(a)
        word = ana[0]
        a = re.sub(r"[^A-Za-zА-Яа-я]+", '', a)

        if 'NOUN' not in word.tag and 'ADJF' not in word.tag:
            continue

        lemma = word.normal_form
        case = word.tag.case
        gender = word.tag.gender
        number = word.tag.number
        postfix = ''
        if 'NOUN' in word.tag:
            postfix = '_S'
        if 'ADJF' in word.tag:
            postfix = '_A'

        lemma_m = lemma + postfix

        if lemma_m in model:
            new_word = ''
            for n_w in model.most_similar(positive=[lemma_m], topn=50):
                if postfix in n_w[0]:
                    new_word = n_w[0]
                    break

            new_word = new_word.split('_')[0]
            modified = morph.parse(new_word)[0]
            if modified.inflect({case}) is not None:
                modified = modified.inflect({case})
            if modified.inflect({number}) is not None:
                modified = modified.inflect({number})
            if gender is not None and modified.inflect({gender}) is not None:
                modified = modified.inflect({gender})
            final = modified.word
            if isUpper:
                final = final.title()
            phrase = phrase.replace(a, final)
        else:
            continue

    smart_quote['phrase'] = phrase
    smart_quote['original'] = False

    return smart_quote
