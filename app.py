from datetime import date, datetime
from flask import Flask, request, redirect, render_template, flash, url_for, get_template_attribute
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
from sqlalchemy.orm import session, scoped_session, sessionmaker
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
Flask.debug = True
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' \
                                        + os.path.join(basedir, 'mybd.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '<the super secret key comes here>'
db = SQLAlchemy(app)

from entities import *

''' Словарь для того, чтобы можно было брать нужные данные в html'''

tables = {"Клиенты": [Client, 1, 'null', "клиента", " клиенте", "ФИО"],
          "Авто": [Auto, 2, Client, "авто", "б авто", "Марка или номер"],
          "Заказы": [Orderr, 3, Auto, "заказ", " заказе", "Описание"],
          "Сотрудники": [Worker, 4, 'null', "сотрудника", " сотруднике", "ФИО или должность"],
          "Запчасти": [Spare, 5, Defect, "запчасть", " запчасти", "Название или марка"],
          "Неисправности": [Defect, 6, 'null', "неисправность", " неисправности", "Название"]
          }


@app.route('/')
def index():
    return render_template("start_page.html")


@app.route('/bd')
def table_page():
    return render_template("bd.html")


@app.route('/bd/table', methods=['GET'])
def table_work():
    global tname  # переменная для правильного выбора таблицы при переходе страниц
    tname = request.args['table']
    table = tables[tname][0]
    n = tables[tname][1]
    item = tables[tname][3]
    ag = aggreg(tname)
    if request.args['button'] == "Показать":
        key_name = tables[tname][5]
        return render_template('show_table.html', table=table.query.all(), tname=tname, n=n, key_name=key_name, ag=ag)

    elif request.args['button'] == "Добавить":
        key = tables[tname][2]
        if key == 'null':
            return render_template('page_add.html', n=n, key=key, item=item)
        else:
            return render_template('page_add.html', n=n, key=key.query.all(), item=item)

    elif request.args['button'] == "Изменить":
        item_1 = tables[tname][4]
        return render_template('page_update.html', n=n, table=table.query.all(), item=item, item_1=item_1)

    elif request.args['button'] == "Удалить":
        return render_template('page_delete.html', n=n, item=item, table=table.query.all())


@app.route('/bd/new', methods=['GET', 'POST'])
def add():
    table = tables[tname][0]
    n = tables[tname][1]
    key_name = tables[tname][5]
    key = tables[tname][2]
    if request.method == 'POST':
        if request.form['button'] == "Добавить клиента":  # Клиент
            if not request.form['name'] or not request.form['phone_number']:
                flash('Заполните, пожалуйста, все поля!', 'error')
            else:
                it = Client(request.form['name'], str(request.form['phone_number']))
                bd_add(it)
                ag = aggreg(tname)
                return render_template('show_table.html', table=table.query.all(), tname=tname, n=n, key_name=key_name,
                                       ag=ag)

        elif request.form['button'] == "Добавить авто":  # Авто
            if not request.form['brand'] or not request.form['number'] or not request.form['color'] \
                    or not request.form['release_date']:
                flash('Заполните, пожалуйста, все поля!', 'error')
            else:
                client_id = int(request.form['key'])
                release_date = datetime.datetime.strptime(request.form['release_date'], '%Y-%m-%d')
                it = Auto(request.form['brand'], request.form['number'],
                          request.form['color'], release_date, client_id)
                bd_add(it)
                ag = aggreg(tname)
                return render_template('show_table.html', table=table.query.all(), tname=tname, n=n, key_name=key_name,
                                       ag=ag)

        elif request.form['button'] == "Добавить заказ":  # Заказ
            if not request.form['reg_date'] or not request.form['description']:
                flash('Заполните, пожалуйста, все поля!', 'error')
            else:
                auto_id = int(request.form['key'])
                reg_date = datetime.datetime.strptime(str(request.form['reg_date']), '%Y-%m-%d')
                complete_date = datetime.datetime.strptime(str(request.form['complete_date']), '%Y-%m-%d')
                it = Orderr(request.form['description'], reg_date, complete_date, auto_id)
                bd_add(it)
                ag = aggreg(tname)
                return render_template('show_table.html', table=table.query.all(), tname=tname, n=n, key_name=key_name,
                                       ag=ag)

        elif request.form['button'] == "Добавить сотрудника":  # Сотрудник
            if not request.form['name'] or not request.form['birthdate'] or not request.form['salary'] \
                    or not request.form['position']:
                flash('Заполните, пожалуйста, все поля!', 'error')
            else:
                birthdate = datetime.datetime.strptime(request.form['birthdate'], '%Y-%m-%d')
                it = Worker(request.form['name'], birthdate, request.form['salary'], request.form['position'],
                            request.form['operation_mode'])
                bd_add(it)
                ag = aggreg(tname)
                return render_template('show_table.html', table=table.query.all(), tname=tname, n=n, key_name=key_name,
                                       ag=ag)

        elif request.form['button'] == "Добавить запчасть":  # Запчасть
            if not request.form['name'] or not request.form['label'] or not request.form['cost']:
                flash('Заполните, пожалуйста, все поля!', 'error')
            else:
                defect_id = int(request.form['key'])
                it = Spare(request.form['name'], request.form['label'], request.form['cost'], defect_id)
                bd_add(it)
                ag = aggreg(tname)
                return render_template('show_table.html', table=table.query.all(), tname=tname, n=n, key_name=key_name,
                                       ag=ag)

        elif request.form['button'] == "Добавить неисправность":  # Неисправность
            if not request.form['name']:
                flash('Заполните, пожалуйста, все поля!', 'error')
            else:
                it = Defect(request.form['name'])
                bd_add(it)
                ag = aggreg(tname)
                return render_template('show_table.html', table=table.query.all(), tname=tname, n=n, key_name=key_name,
                                       ag=ag)
    if key == "null":
        return render_template('page_add.html', n=n, key=key)
    return render_template('page_add.html', n=n, key=key.query.all())


def bd_add(item):
    db.session.add(item)
    db.session.commit()
    flash('Запись была успешно добавлена!')


@app.route('/bd/update', methods=['GET', 'POST'])  # ИЗМЕНЕНИЕ
def update():
    if request.method == 'POST':
        table = tables[tname][0]
        n = tables[tname][1]
        key_name = tables[tname][5]
        if request.form['button'] == "Изменить клиента":
            it = Client.query.get(request.form['items'])
            if request.form['name']:
                it.name = request.form['name']
            it.phone_number = request.form['phone_number']

        elif request.form['button'] == "Изменить авто":
            it = Auto.query.get(request.form['items'])
            if request.form['brand']:
                it.brand = request.form['brand']
            if request.form['number']:
                it.number = request.form['number']
            it.color = request.form['color']
            if request.form['release_date']:
                it.release_date = datetime.datetime.strptime(request.form['release_date'], '%Y-%m-%d')

        elif request.form['button'] == "Изменить заказ":
            it = Orderr.query.get(request.form['items'])
            it.description = request.form['description']
            if request.form['reg_date']:
                it.reg_date = datetime.datetime.strptime(request.form['reg_date'], '%Y-%m-%d')

        elif request.form['button'] == "Изменить сотрудника":
            it = Worker.query.get(request.form['items'])
            if request.form['name']:
                it.name = request.form['name']
            if request.form['birthdate']:
                it.birthdate = datetime.datetime.strptime(str(request.form['birthdate']), '%Y-%m-%d')
            if request.form['salary']:
                it.salary = float(request.form['salary'])
            if request.form['position']:
                it.position = request.form['position']
            if request.form['operation_mode']:
                it.position = request.form['operation_mode']

        elif request.form['button'] == "Изменить запчасть":
            it = Spare.query.get(request.form['items'])
            if request.form['name']:
                it.name = request.form['name']
            if request.form['cost']:
                it.cost = float(request.form['cost'])
            it.label = request.form['label']
        elif request.form['button'] == "Изменить неисправность":
            it = Defect.query.get(request.form['items'])
            if request.form['name']:
                it.name = request.form['name']
        db.session.commit()
        ag = aggreg(tname)
        return render_template('show_table.html', table=table.query.all(), tname=tname, n=n, key_name=key_name, ag=ag)
    return redirect(url_for('table_page'))


@app.route('/bd/delete', methods=['GET'])
def delete():
    table = tables[tname][0]
    n = tables[tname][1]
    key_name = tables[tname][5]
    if request.args['button'] == "Удалить клиента":
        it = Client.query.get(request.args['items'])
    elif request.args['button'] == "Удалить авто":
        it = Auto.query.get(request.args['items'])
    elif request.args['button'] == "Удалить заказ":
        it = Orderr.query.get(request.args['items'])
    elif request.args['button'] == "Удалить сотрудника":
        it = Worker.query.get(request.args['items'])
    elif request.args['button'] == "Удалить запчасть":
        it = Spare.query.get(request.args['items'])
    elif request.args['button'] == "Удалить неисправность":
        it = Defect.query.get(request.args['items'])
    db.session.delete(it)
    db.session.commit()
    ag = aggreg(tname)
    return render_template('show_table.html', table=table.query.all(), tname=tname, n=n, key_name=key_name, ag=ag)


@app.route('/bd/find', methods=['GET'])
def find():
    n = tables[tname][1]
    key_name = tables[tname][5]
    ag = aggreg(tname)
    if not request.args['pattern']:
        table = tables[tname][0].query.all()
        flash("Введите, пожалуйста, запрос для поиска!", "error")
    else:
        s = '%' + request.args['pattern'] + '%'
        if tname == "Клиенты":
            table = db.session.query(Client).filter(Client.name.like(s)).all()
        elif tname == "Авто":
            table = db.session.query(Auto).filter(or_(Auto.brand.like(s), Auto.number.like(s))).all()
        elif tname == "Заказы":
            table = db.session.query(Orderr).filter(Orderr.description.like(s)).all()
        elif tname == "Сотрудники":
            table = db.session.query(Worker).filter(or_(Worker.name.like(s), Worker.position.like(s))).all()
        elif tname == "Запчасти":
            table = db.session.query(Spare).filter(or_(Spare.name.like(s), Spare.label.like(s))).all()
        elif tname == "Неисправности":
            table = db.session.query(Defect).filter(Defect.name.like(s)).all()
    return render_template('show_table.html', table=table, tname=tname, n=n, key_name=key_name, ag=ag)


def aggreg(t_name):
    res = list()
    if t_name == "Клиенты":
        # ag = Client.query.count()          альтернативный запрос
        ag = db.session.query(func.count(Client.client_id)).scalar()
        res.append('Количество клиентов в базе данных: ' + str(ag))
    elif t_name == "Авто":
        ag1 = db.session.query(Auto).filter(Auto.release_date > '2009-12-31').count()
        ag2 = db.session.query(Auto).filter(Auto.release_date <= '2010-12-31').count()
        res.append("Выпуска до 2010 года: " + str(ag2) + " авто")
        res.append("Выпуска позже 2010 года: " + str(ag1) + " авто")
    elif t_name == "Заказы":
        ag = db.session.query(Orderr).filter(
            Orderr.complete_date == db.session.query(func.max(Orderr.complete_date))).first()
        res.append("Последний завершённый заказ: " + ag.description + " - " + str(ag.complete_date.day) + '.' \
                   + str(ag.complete_date.month) + '.' + str(ag.complete_date.year))
    elif t_name == "Запчасти":
        ag1 = db.session.query(Spare).filter(Spare.cost == db.session.query(func.max(Spare.cost))).first()
        ag2 = db.session.query(Spare).filter(Spare.cost == db.session.query(func.min(Spare.cost))).first()
        res.extend(["Наивысшая стоимость запчасти: " + str(ag1.cost) + " - " + str(
            ag1.name + " " + ag1.label), "\n Наименьшая стоимость запчасти: " \
                    + str(ag2.cost) + " - " + str(ag2.name + " " + ag2.label)])
    elif t_name == "Сотрудники":
        ag = db.session.query(func.avg(Worker.salary)).scalar()
        res.append("Средний оклад: " + str(ag) + " руб.")
    elif t_name == "Неисправности":
        ag = db.session.query(func.count(Defect.defect_id)).scalar()
        res.append("Кол-во в базе: " + str(ag))
    return res


@app.route('/about')
def about():
    return render_template("proger_page.html")


@app.route('/contacts')
def contacts_page():
    return render_template("contacts_page.html")


if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)


# if tname == "Авто" or tname == "Заказ" or tname == "Запчасть":
#     for it in table.query.all():
#         if tname == "Авто":
#             it.fk_name = Client.query.get(it.client_id).name
#         elif tname == "Заказ":
#             it.fk_name = Auto.query.get(it.auto_id).brand
#         else:
#             it.fk_name = Defect.query.get(it.defect_id).name
#         db.session.commit()
# tb = session.query(Client, Auto).filter(Client.client_d == Auto.client_id).all()


''' метод для создания имён внешних ключей (но он не нужен. ибо есть backref'''# def aggreg(t_name):
#     if t_name == "Клиенты":
#         # ag = Client.query.count()          альтернативный запрос
#         ag = db.session.query(func.count(Client.client_id)).scalar()
#         res = 'Количество клиентов в базе данных: ' + str(ag)
#     elif t_name == "Авто":
#         ag1 = db.session.query(Auto).filter(Auto.release_date > '2009-12-31').count()
#         ag2 = db.session.query(Auto).filter(Auto.release_date <= '2010-12-31').count()
#         res = "Выпуска до 2010 года: " + str(ag2) + " авто" \
#               + '<br>' + "Выпуска позже 2010 года: " + str(ag1) + " авто"
#     elif t_name == "Заказы":
#         ag = db.session.query(Orderr).filter(
#             Orderr.complete_date == db.session.query(func.max(Orderr.complete_date))).first()
#         res = "Последний завершённый заказ: " + ag.description + " - " + str(ag.complete_date.day) + '.' \
#               + str(ag.complete_date.month) + '.' + str(ag.complete_date.year)
#     elif t_name == "Запчасти":
#         ag1 = db.session.query(Spare).filter(Spare.cost == db.session.query(func.max(Spare.cost))).first()
#         ag2 = db.session.query(Spare).filter(Spare.cost == db.session.query(func.min(Spare.cost))).first()
#         res = "Наивысшая стоимость запчасти: " + str(ag1.cost) + " - " + str(
#             ag1.name + " " + ag1.label) + "\n Наименьшая стоимость запчасти: " \
#               + str(ag2.cost) + " - " + str(ag2.name + " " + ag2.label)
#     elif t_name == "Сотрудники":
#         ag = db.session.query(func.avg(Worker.salary)).scalar()
#         res = "Средний оклад: " + str(ag) + " руб."
#     elif t_name == "Неисправности":
#         ag = db.session.query(func.count(Defect.defect_id)).scalar()
#         res = "Кол-во в базе: " + str(ag)
#     return res
