from flask import Flask, render_template, request, redirect, session
from db import *
import hashlib, random, os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates', static_folder='templates/static')
app.secret_key = os.urandom(30).hex()
app.config['JWT_SECRET_KEY'] = 'super-secret'

if len(take_accesses()) == 0:
    i = 0
    accesses = [["public","Публичный"],["general","Общий"],["private","Приват"]]
    while i < len(accesses):
        add_accesses(accesses[i][0],accesses[i][1])
        i = i + 1

@app.route('/', methods=['post', 'get'])
def index():
    long_link = request.form.get('long_link')
    accesses = request.form.get('accesses')
    pseudonym = request.form.get('pseudonym')
    massage = ''
    short_link = ''
    hosthref = request.host_url
    if long_link != None and long_link != "":
        if 'user' in session:
            userLongLink = take_long_user(long_link, session['user'])
            if len(userLongLink) == 0:
                if pseudonym:
                    checkPseudonym = take_pseudonym(pseudonym)
                    if len(checkPseudonym) == 0:
                        short_link = hosthref + "host/" + pseudonym
                        add_link(long_link, pseudonym, accesses, session['user'])
                    else:
                        massage = 'Этот псевдоним уже занят'
                else:
                    user_short_link = hashlib.md5(long_link.encode()).hexdigest()[:random.randint(8, 12)]
                    short_link = hosthref + "host/" + user_short_link
                    add_link(long_link,user_short_link,accesses,session['user'])
            else:
                massage = 'Вы уже сокращали эту ссылку'
        else:
            if pseudonym:
                checkPseudonym = take_pseudonym(pseudonym)
                if len(checkPseudonym) == 0:
                    short_link = hosthref + "host/" + pseudonym
                    add_link(long_link, pseudonym, accesses, None)
                else:
                    massage = 'Этот псевдоним уже занят'
            else:
                user_short_link = hashlib.md5(long_link.encode()).hexdigest()[:random.randint(8, 12)]
                short_link = hosthref + "host/" + user_short_link
                add_link(long_link, user_short_link, accesses, None)
    return render_template("index.html", massage=massage, short_link=short_link)

@app.route('/auth', methods=['post', 'get'])
def auth():
    massage = ''
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        if login != "" and password != "":
            user = take_user(login)
            if len(user) > 0:
                if check_password_hash(user[0][0], password) == True:
                    auth_user = take_userId(login)[0]
                    session['user'] = auth_user
                    return redirect('/profile')
                else:
                    massage = 'Вы ввели неверный пароль'
            else:
                massage = 'Такого пользователя нет'
        else:
            massage = 'Вы ввели неверный логин или пароль'

    return render_template("auth.html", massage=massage)

@app.route('/reg', methods=['post', 'get'])
def reg():
    massage = ''
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = take_user(login)
        if login != "" and password != "":
            if len(user) == 0:
                hash_password = generate_password_hash(password)
                registration(login, hash_password)
                auth_user = take_userId(login)[0]
                session['user'] = auth_user
                return redirect('/profile')
            else:
                massage = 'Такой пользователь уже есть'
        else:
            massage = 'Вы ввели неверный логин или пароль'

    return render_template("registr.html", massage=massage)

@app.route('/profile', methods=['post', 'get'])
def profile():
    btn_edit = request.form.get('btn_edit')
    btn_delete = request.form.get('btn_delete')
    links = take_user_links(session['user'])
    hosthref = request.host_url
    massage = ""

    if btn_edit:
        long = request.form.get('long')
        short = request.form.get('short')
        access = request.form.get('access')
        if long != None and short != None:
            if links[0][2] != access and take_pseudonym(short) == 0:
                update_link(long, short, access, session['user'])
                return redirect('/profile')
            else:
                if len(take_pseudonym(short)) > 0:
                    massage = 'Этот псевдоним уже занят'
                else:
                    update_link(long, short, access, session['user'])
                    return redirect('/profile')

    if btn_delete:
        delete_link(btn_delete, session['user'])
        return redirect('/profile')

    return render_template("/profile.html", links=links, hosthref=hosthref, massage=massage)

@app.route('/logout', methods=['post', 'get'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/report')
def message():
    return render_template('/report.html')

@app.route('/404')
def error():
    return render_template('/404.html')

@app.route('/host/<shortlink>')
def link(shortlink):
    if len(take_link_info(shortlink)) != 0:
        user_link = take_link_info(shortlink)[0]
        print(user_link)
        count = user_link[1]
        if user_link[2] == 1:
            update_count(user_link[0],count + 1)
            return redirect(user_link[0])
        elif user_link[2] == 2:
            if 'user' in session:
                update_count(user_link[0], count + 1)
                return redirect(user_link[0])
            else:
                return redirect('/auth')
        elif user_link[2] == 3:
            if 'user' in session:
                if len(take_long_user(user_link[0],session['user'])) > 0:
                    update_count(user_link[0], count + 1)
                    return redirect(user_link[0])
                else:
                    return redirect('/report')
            else:
                return redirect('/report')
        elif user_link[2] == None:
            return redirect('/report')
    else:
        return redirect('/404')

if __name__ == '__main__':
    app.run()