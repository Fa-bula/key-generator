#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, g, redirect, url_for, render_template
from contextlib import closing
import sqlite3
import string
import random

TOTAL_NUMBER_OF_KEYS = (len(string.letters + string.digits)) ** 4
app = Flask(__name__)
app.config.from_pyfile('config.cfg')


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def string_generator(size=4, chars=string.letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_remain_keys_number():
    g.db = connect_db()
    cur = g.db.execute('select count(*) from given_keys')
    return TOTAL_NUMBER_OF_KEYS - cur.fetchall()[0][0]


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def get_key():
    while(True):
        try:
            key = string_generator()
            g.db.execute('insert into given_keys values(?, 0)', [key])
            g.db.commit()
            break
        except sqlite3.IntegrityError:
            pass
    return render_template('index.html', key=key,
                           remain=get_remain_keys_number())


@app.route('/status/<key>')
def getStatus(key):
    cur = g.db.execute('select is_repaid from given_keys where val=?', [key])
    result = cur.fetchall()
    if result == []:
        status = 'еще не выдан'
    else:
        if result[0][0] == 1:
            status = 'уже выдан и погашен'
        else:
            status = 'уже выдан, но еще не погашен'
    return render_template('status.html', key=key,
                           keyStatus=status.decode('utf-8'),
                           remain=get_remain_keys_number())


@app.route('/status/', methods=['GET', 'POST'])
def chooseKeyToGetStatus():
    if request.method == 'POST':
        key = request.form['key']
        return redirect(url_for('getStatus', key=key))

    return render_template('status_choose.html',
                           remain=get_remain_keys_number())


@app.route('/repay/<key>')
def repay(key):
    cur = g.db.execute('select is_repaid from given_keys where val=?', [key])
    result = cur.fetchall()
    if result == []:
        status = ', но такой ключ еще не выдавался'
    else:
        is_repaid = result[0][0]
        if is_repaid == 1:
            status = ', но этот ключ был погашен ранее'
        if is_repaid == 0:
            cur = g.db.execute('update given_keys set is_repaid=1 where val=?',
                               [key])
            g.db.commit()
            status = ' и этот ключ успешно погашен'
    return render_template('repay.html', key=key,
                           keyStatus=status.decode('utf-8'),
                           remain=get_remain_keys_number())


@app.route('/repay/', methods=['GET', 'POST'])
def chooseKeyToRepay():
    if request.method == 'POST':
        key = request.form['key']
        return redirect(url_for('repay', key=key))

    return render_template('repay_choose.html',
                           remain=get_remain_keys_number())


if __name__ == '__main__':
    app.run(host='0.0.0.0')
