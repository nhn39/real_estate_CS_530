from flask import (Flask, g, jsonify, redirect, render_template, request,
                   session)
from passlib.hash import pbkdf2_sha256

from db import Database

DATABASE_PATH = 'goats.db'

app = Flask(__name__)
app.secret_key = b'demokeynotreal!'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = Database(DATABASE_PATH)
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/adopt')
def adopt():
    return render_template('adopt.html')


@app.route('/mygoats')
def mygoats():
    return render_template('mygoats.html')


def generate_get_goats_response(args):
    n = args.get('n', default=6)
    offset = args.get('offset', default=0)
    return jsonify({
        'goats': get_db().get_goats(n, offset),
        'total': get_db().get_num_goats()
    })


@app.route('/api/get_goats', methods=['GET'])
def api_get_goats():
    return generate_get_goats_response(request.args)


@app.route('/api/adopt_goat', methods=['POST'])
def api_adopt():
    if 'user' in session:
        goat_id = request.form.get('goat_id')
        user_id = session['user']['id']
        get_db().update_goat(goat_id, user_id)
        return generate_get_goats_response(request.form)
    else:
        return jsonify('Error: User not authenticated')


def generate_my_goats_response(args):
    user_id = session['user']['id']
    goats = get_db().get_user_goats(user_id)
    return jsonify({
        'goats': goats,
        'total': len(goats),
    })


@app.route('/api/my_goats', methods=['GET'])
def api_my_goats():
    if 'user' in session:
        return generate_my_goats_response(request.args)
    else:
        return jsonify('Error: User not authenticated')


@app.route('/api/unadopt_goat', methods=['POST'])
def api_unadopt():
    if 'user' in session:
        goat_id = request.form.get('goat_id')
        get_db().update_goat(goat_id, -1)
        return generate_my_goats_response(request.form)
    else:
        return jsonify('Error: User not authenticated')


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        typed_password = request.form.get('password')
        if name and username and typed_password:
            encrypted_password = pbkdf2_sha256.hash(typed_password)
            get_db().create_user(name, username, encrypted_password)
            return redirect('/login')
    return render_template('create_user.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        typed_password = request.form.get('password')
        if username and typed_password:
            user = get_db().get_user(username)
            if user:
                if pbkdf2_sha256.verify(typed_password, user['encrypted_password']):
                    session['user'] = user
                    return redirect('/')
                else:
                    message = "Incorrect password, please try again"
            else:
                message = "Unknown user, please try again"
        elif username and not typed_password:
            message = "Missing password, please try again"
        elif not username and typed_password:
            message = "Missing username, please try again"
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
