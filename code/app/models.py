from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    deals = db.relationship('Deal', backref='user', lazy=True)
    cart_items = db.relationship('Cart', backref='user', lazy=True)
    ssh_keys = db.relationship('SSHKey', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class ConfTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    os = db.Column(db.String(45))
    description = db.Column(db.String(256))
    photo = db.Column(db.String(256))
    cores = db.Column(db.Integer)
    cpu_freq = db.Column(db.Float)
    gpu_cores = db.Column(db.Integer)
    cuda = db.Column(db.Integer)
    gpu_freq = db.Column(db.Integer)
    ram_mem = db.Column(db.Integer)
    ram_freq = db.Column(db.Integer)
    memory = db.Column(db.Integer)
    price = db.Column(db.Integer)
    discount = db.Column(db.Integer)

class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cores = db.Column(db.Integer)
    cpu_freq = db.Column(db.Float)
    gpu_cores = db.Column(db.Integer)
    cuda = db.Column(db.Integer)
    gpu_freq = db.Column(db.Integer)
    ram_mem = db.Column(db.Integer)
    ram_freq = db.Column(db.Integer)
    memory = db.Column(db.Integer)
    vm = db.relationship('VM', backref='configuration', uselist=False)

class VM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    os = db.Column(db.String(45))
    description = db.Column(db.String(256))
    photo = db.Column(db.String(256))
    price = db.Column(db.Integer)
    status = db.Column(db.String(45), default='Stopped')
    id_conf = db.Column(db.Integer, db.ForeignKey('configuration.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ssh_key = db.relationship('SSHKey', backref='vm', uselist=False)
    discount = db.Column(db.String(45))

    id_conf_templates = db.Column(db.Integer, db.ForeignKey('conf_template.id'))


class SSHKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vm_id = db.Column(db.Integer, db.ForeignKey('vm.id'))
    key_content = db.Column(db.Text)


class Deal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vm_id = db.Column(db.Integer, db.ForeignKey('vm.id'))
    amount = db.Column(db.Integer)
    date_start = db.Column(db.String(12))
    date_finish = db.Column(db.String(12))

    vm = db.relationship('VM', backref='deals')

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vm_id = db.Column(db.Integer, db.ForeignKey('vm.id'))
    quantity = db.Column(db.Integer, default=1)

    vm = db.relationship('VM', backref='cart_items')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vm_id = db.Column(db.Integer, db.ForeignKey('vm.id'))
    amount = db.Column(db.Integer)
    payment_info = db.Column(db.String(256))
    status = db.Column(db.String(45), default='Paid')

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(45))

class VMService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vm_id = db.Column(db.Integer, db.ForeignKey('vm.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

class ServiceHasConfTemplate(db.Model):
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), primary_key=True)
    conf_template_id = db.Column(db.Integer, db.ForeignKey('conf_template.id'), primary_key=True)

