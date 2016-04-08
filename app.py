#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
import sqlite3
import string
import random

app = Flask(__name__)
app.config.from_pyfile('config.cfg')


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def string_generator(size=4, chars=string.letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


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
    return key


@app.route('/status/<key>')
def get_status(key):
    cur = g.db.execute('select is_repaid from given_keys where val=?', [key])
    result = cur.fetchall()
    print(result)
    if result == []:
        return 'не выдан'
    else:
        if result == 1:
            return 'погашен'
        else:
            return 'выдан'


@app.route('/repay/<key>')
def repay(key):
    cur = g.db.execute('select is_repaid from given_keys where val=?', [key])
    result = cur.fetchall()
    if result == []:
        return 'Такой ключ еще не выдавался'
    is_repaid = result[0][0]
    if is_repaid == 1:
        return 'Этот ключ был погашен ранее'
    if is_repaid == 0:
        cur = g.db.execute('update given_keys set is_repaid=1 where val=?', [key])
        g.db.commit()
        return 'Ключ успешно погашен'

if __name__ == '__main__':
    app.run()
