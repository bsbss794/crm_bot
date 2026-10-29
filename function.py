import sqlite3
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

DB_FILE = 'crmmini_database.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
                    CREATE TABLE IF NOT EXISTS Client (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_user INTEGER NOT NULL,
                        name TEXT NOT NULL
                    )
                ''')

        # Создаём таблицу Order (исправление: внешний ключ на id в таблице Client)
        c.execute('''
                    CREATE TABLE IF NOT EXISTS Orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_user INTEGER NOT NULL,
                        client_id INTEGER REFERENCES Client(id) ON DELETE SET NULL,
                        "order" TEXT NOT NULL,
                        price INTEGER NOT NULL,
                        status TEXT DEFAULT 'now',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

        c.execute('''
                    CREATE TABLE IF NOT EXISTS Remembers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_user INTEGER NOT NULL,
                        "order" INTEGER REFERENCES Orders(id) ON DELETE SET NULL,
                        status TEXT DEFAULT 'now',
                        target_time TIMESTAMP NOT NULL
                    )
                ''')

        conn.commit()

def add_client(client_data):
    # client_data должен содержать: id_user, name, order, price
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            '''INSERT INTO Client (id_user, name)
               VALUES (?, ?)''',
            (client_data['id_user'], client_data['name'])
        )
        conn.commit()
        return f"клиент создан. id: {c.lastrowid}" # вернёт id новой записи, если понадобится

def get_clients(id_user):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            '''SELECT id, id_user, name FROM Client WHERE id_user = ?''', (id_user,)
        )
        conn.commit()
        result = c.fetchall()
        return result

def get_orders_func(id_user):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            '''SELECT id,client_id, "order", price, status, created_at FROM Orders WHERE id_user = ?''', (id_user,)
        )
        conn.commit()
        result = c.fetchall()
        return result

def del_client(name, id_user):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            '''DELETE FROM Client WHERE name = ? AND id_user = ?''', (name, id_user)
        )
        conn.commit()
        return "успешное удаление"

def del_order(name):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            '''DELETE FROM Orders WHERE id = ?''', (int(name),)
        )
        conn.commit()
        return "успешное удаление"

def suc_order(name, id_user):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            '''UPDATE Orders SET status = 'success' WHERE id = ? AND id_user = ?''', (name, id_user)
        )
        conn.commit()
        return "успешное выполнение!"

def pay_order(name, id_user):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            '''UPDATE Orders SET status = 'payed' WHERE id = ? AND id_user = ?''', (name, id_user)
        )
        conn.commit()
        return "успешная оплата!"

def add_order_func(order_data):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            '''INSERT INTO Orders (id_user, client_id, "order", price)
               VALUES (?, ?, ?, ?)''',
            (order_data['id_user'], order_data['client_id'], order_data['order'], order_data['price'])
        )
        conn.commit()
        return f"заказ создан. id: {c.lastrowid}"  # вернёт id новой записи, если понадобится

def add_remembers_func(remembers_data):
    if remembers_data['time'] == "":
        target_time = datetime.now() + timedelta(days=1)
    else:
        target_time = datetime.now() + timedelta(days=int(remembers_data['time']))
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            '''INSERT INTO Remembers (id_user, "order", status, target_time)
               VALUES (?, ?, ?, ?)''',
            (remembers_data['id_user'], remembers_data['order'], "not", target_time)
        )
        conn.commit()
        return c.lastrowid  # вернёт id новой записи, если понадобится

def send(user_id, order_id, remeber_id):
    from CRMmini import bot
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''SELECT status FROM Remembers WHERE id=?''', (remeber_id,))
            conn.commit()
            if c.fetchone()[0][0] == "not":
                return

        text = f"у вас незаконченный заказ: {order_id}"

        bot.send_message(user_id, text)

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''UPDATE Remembers SET status='yes' WHERE id=?''', (remeber_id,))
            conn.commit()
            return
    except Exception as e:
        print(e)

def check_upcoming_appointments():
    print('ищу напоминания')
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''SELECT id, id_user, "order", status, target_time FROM Remembers WHERE status="not"''',)
        conn.commit()
        result = c.fetchall()

    for r in result:
        if datetime.now() > datetime.strptime(r[4], "%Y-%m-%d %H:%M:%S.%f"):
            send(r[1], r[2], r[0])
            print('напоминаю')

def start_scheduler():
    """Запускает фоновый планировщик"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_upcoming_appointments, 'interval', minutes=1)
    scheduler.start()
    print("✅ Планировщик напоминаний запущен!")
    return scheduler
