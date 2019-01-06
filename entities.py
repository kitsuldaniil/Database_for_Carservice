from app import *
# make constructors


class Client(db.Model):
    __tablename__ = 'client'
    client_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(50), unique=True)

    auto = db.relationship('Auto', backref='client')

    def __init__(self, name, phone_number):
        self.name = name
        self.phone_number = phone_number

    def __repr__(self):
        return '<Client %r>' % self.name


class Auto(db.Model):
    __tablename__ = 'auto'
    auto_id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), unique=True)
    brand = db.Column(db.String(50))
    color = db.Column(db.String(50))
    release_date = db.Column(db.Date())

    def __init__(self, brand, number, color, release_date, client_id):
        self.brand = brand
        self.number = number
        self.color = color
        self.release_date = release_date
        self.client_id = client_id
        # cl = Client.query.get(self.client_id)
        #self.fk_name = '111'

    def __repr__(self):
        return '<Auto %r>' % self.brand
    orders = db.relationship('Orderr', backref='auto')
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'))


defect_in_order = db.Table('defect_in_order',
                        db.Column('num_or', db.Integer, db.ForeignKey('orderr.num_or')),
                        db.Column('defect_id', db.Integer, db.ForeignKey('defect.defect_id')))


class Orderr(db.Model):
    __tablename__ = 'orderr'
    num_or = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=True)
    reg_date = db.Column(db.Date)
    complete_date = db.Column(db.Date, nullable=True)

    auto_id = db.Column(db.Integer, db.ForeignKey('auto.auto_id'))

    defects = db.relationship('Defect', secondary=defect_in_order,
                              backref=db.backref('orderr', lazy='dynamic'),
                              lazy='dynamic')

    def __init__(self, description, reg_date, complete_date, auto_id):
        self.description = description
        self.reg_date = reg_date
        self.complete_date = complete_date
        self.auto_id = auto_id

    def __repr__(self):
        return '<Order %r>' % self.id


class Defect(db.Model):
    __tablename__ = 'defect'
    defect_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    spares = db.relationship('Spare', backref='defect')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Defect %r>' % self.name


worker_order = db.Table('worker_order',
                        db.Column('worker_id', db.Integer, db.ForeignKey('worker.worker_id')),
                        db.Column('num_or', db.Integer, db.ForeignKey('orderr.num_or')))


class Worker(db.Model):
    __tablename__ = 'worker'
    worker_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    birthdate = db.Column(db.Date)
    salary = db.Column(db.Float, nullable=True)
    position = db.Column(db.String(50))
    operation_mode = db.Column(db.String(50))

    def __init__(self, name, birthdate, salary, position, operation_mode):
        self.name = name
        self.birthdate = birthdate
        self.salary = salary
        self.position = position
        self.operation_mode = operation_mode

    orders = db.relationship('Orderr', secondary=worker_order,
                             backref=db.backref('worker', lazy='dynamic'),
                             lazy='dynamic')


class Spare(db.Model):
    __tablename__ = 'spare'
    spare_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    label = db.Column(db.String(50))
    cost = db.Column(db.Float, nullable=True)

    defect_id = db.Column(db.Integer, db.ForeignKey('defect.defect_id'))

    #fk_name = '222'

    def __init__(self, name, label, cost, defect_id):
        self.name = name
        self.label = label
        self.cost = cost
        self.defect_id = defect_id

    def __repr__(self):
        return '<Spare %r>' % self.name


def add(title_of_table):
    """Добавление в бд"""
    try:
        new_row = eval(title_of_table)()
        db.session.add(new_row)
        db.session.flush()
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def delete(delete_id, title_of_table):
    """Удаление из бд"""
    obj_for_delete = eval(title_of_table).query.get(delete_id)
    db.session.delete(obj_for_delete)
    db.session.flush()
    db.session.commit()


def update(value, update_id, attr_title, title_of_table):
    """Редактирование в бд"""
    print(update_id)
    obj_for_update = eval(title_of_table).query.get(update_id)
    setattr(obj_for_update, attr_title, value)
    db.session.flush()
    db.session.commit()


def get_fk(table, id):
    res = table.query.get(id)
    return res
