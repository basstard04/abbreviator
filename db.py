import sqlite3

connect = sqlite3.connect('database.db', check_same_thread=False)
cursor = connect.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS "users"
("id" INTEGER NOT NULL,
"login" TEXT NOT NULL,
"password" TEXT NOT NULL,
primary key ("id" AUTOINCREMENT)
);''')
connect.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS "links"
("id" INTEGER NOT NULL,
"long" TEXT NOT NULL,
"short" TEXT NOT NULL,
"access_id" INTEGER NOT NULL,
"owner_id" INTEGER NOT NULL,
primary key ("id" AUTOINCREMENT)
);''')
connect.commit()

cursor.execute('''CREATE TABLE IF NOT EXISTS "accesses"
("id" INTEGER NOT NULL,
"level_eng" TEXT NOT NULL,
"level_ru" TEXT NOT NULL,
primary key ("id" AUTOINCREMENT)
);''')
connect.commit()

#регистрация
def registration(login,password):
    cursor.execute('''INSERT INTO
        users (login,password)
        VALUES (?,?) 
        ''', (login,password,))
    connect.commit()

def searchUser(login):
    return cursor.execute('''SELECT password 
        FROM users
        WHERE login = ? 
        ''', (login,)).fetchone()

def searchUserId(login):
    return cursor.execute('''SELECT id 
        FROM users
        WHERE login = ? 
        ''', (login,)).fetchone()

def auth(login,password):
    cursor.execute('''SELECT * 
        FROM users
        WHERE login = ? 
        AND password = ?
        ''', (login, password,)).fetchone()
    return "Вы вошли"

def addLink(long,short,access_id,owner_id):
    cursor.execute('''INSERT INTO
        links (long,short,access_id,owner_id)
        VALUES (?,?,?,?)
        ''', (long,short,access_id,owner_id))
    connect.commit()

def seacrAccesses():
    return cursor.execute('''SELECT * FROM accesses
    ''',()).fetchall()

def addAccesses(level_eng,level_ru):
    cursor.execute('''INSERT INTO
        accesses (level_eng,level_ru)
        VALUES (?,?)
        ''', (level_eng,level_ru))
    connect.commit()
    return "Добавление категории прошло успешно"

def searchUserLinks(user_id):
    return cursor.execute('''SELECT links.long, links.short, accesses.level_ru
    FROM links
    INNER JOIN accesses ON accesses.id = links.access_id
    WHERE links.owner_id = ?
    ''', (user_id,)).fetchall()
