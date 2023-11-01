from flask import Flask, render_template, request, redirect, session
from db import *
import hashlib, random, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates', static_folder='templates/static')
app.secret_key = os.urandom(30).hex()
app.config['JWT_SECRET_KEY'] = 'super-secret'

if len(seacrAccesses()) == 0:
    i = 0
    accesses = [["public","публичный"],["private","приватный"],["general","общий"]]
    while i < len(accesses):
        addAccesses(accesses[i][0],accesses[i][1])
        i = i + 1

@app.route('/', methods=['post', 'get'])
def index():
    long_link = request.form.get('long_link')
    accesses = request.form.get('accesses')
    massage = ''
    if long_link != None:
        if 'user' in session:
            user_short_link = ""
            user_short_link = hashlib.md5(long_link.encode()).hexdigest()[:random.randint(8, 12)]
            addLink(long_link,user_short_link,accesses,session['user'])
        else:
            massage = 'войдите, чтобы использовать сокращатель'
    return render_template("index.html", massage=massage)

@app.route('/auth', methods=['post', 'get'])
def auth():
    massage = ''
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = searchUser(login)
        if login != "" and password != "":
            if len(user) != 0:
                if check_password_hash(user[0], password) == True:
                    massage = 'вы успешно вошли'
                    auth_user = searchUserId(login)[0]
                    session['user'] = auth_user
                    return redirect('/profile')
                else:
                    massage = 'неверный пароль'
            else:
                massage = 'такого пользователя нет'
        else:
            massage = 'ваш логин или пароль неправильный'

    return render_template("auth.html", massage=massage)

@app.route('/reg', methods=['post', 'get'])
def reg():
    massage = ''
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirm_password')
        user = searchUser(login)
        if login != "" and password != "":
            if user == None:
                if confirmPassword == password:
                    hash_password = generate_password_hash(password)
                    registr(login, hash_password)
                else:
                    massage = 'пароли не совпадают'
            else:
                massage = 'такой пользователь уже есть'
        else:
            massage = 'ваш логин или пароль неправильный'

    return render_template("registr.html", massage=massage)

@app.route('/profile', methods=['post', 'get'])
def profile():
    userlinks = searchUserLinks(session['user'])
    return render_template("/profile.html", userlinks=userlinks)

if __name__ == '__main__':
    app.run()