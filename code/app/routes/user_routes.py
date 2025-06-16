from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import login_required, current_user
from app.forms import VMCreateForm
from app.models import Configuration, VM, Cart, SSHKey, Payment, Deal, ConfTemplate, Service, VMService
from app import db
from app.security import validate_form_fields
import io
import secrets
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta



bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/create_vm', methods=['GET', 'POST'])
@login_required
def create_vm():
    if request.method == 'POST':
        validate_form_fields(request.form)

        try:
            cores = int(request.form['cores'])
            cpu_freq = float(request.form['cpu_freq'])
            gpu_cores = int(request.form['gpu_cores'])
            cuda = int(request.form['cuda'])
            gpu_freq = float(request.form['gpu_freq'])
            ram_mem = int(request.form['ram_mem'])
            ram_freq = int(request.form['ram_freq'])
            memory = int(request.form['memory'])
        except (KeyError, ValueError):
            flash('Неверные данные формы', 'danger')
            return redirect(url_for('user.create_vm'))

        config = Configuration(
            cores=cores,
            cpu_freq=cpu_freq,
            gpu_cores=gpu_cores,
            cuda=cuda,
            gpu_freq=gpu_freq,
            ram_mem=ram_mem,
            ram_freq=ram_freq,
            memory=memory
        )
        db.session.add(config)
        db.session.commit()

        price = (
            cores * 10 +
            cpu_freq * 5 +
            gpu_cores * 15 +
            cuda * 0.05 +
            gpu_freq * 0.02 +
            ram_mem * 2 +
            ram_freq * 0.01 +
            memory * 0.1
        )
        price = round(price)

        vm = VM(
            os=request.form.get('os', 'Custom'),
            description=request.form.get('description', 'Пользовательская конфигурация'),
            photo=request.form.get('photo', 'custom.png'),
            price=price,
            id_conf=config.id,
            user_id=current_user.id,
            status='In Cart'
        )
        db.session.add(vm)
        db.session.commit()

        service_names = request.form.getlist('services')
        for service_name in service_names:
            name = service_name.strip()
            if not name:
                continue
            service = Service.query.filter_by(service_name=name).first()
            if not service:
                service = Service(service_name=name)
                db.session.add(service)
                db.session.commit()
            link = VMService(service_id=service.id, vm_id=vm.id)
            db.session.add(link)
        db.session.commit()

        cart_item = Cart(user_id=current_user.id, vm_id=vm.id)
        db.session.add(cart_item)
        db.session.commit()

        flash('Виртуальная машина добавлена в корзину', 'success')
        return redirect(url_for('user.cart'))

    return render_template('create_vm_user.html')

@bp.route('/add_to_cart/<int:template_id>', methods=['POST'])
@login_required
def add_to_cart(template_id):
    template = ConfTemplate.query.get_or_404(template_id)

    conf = Configuration(
        cores=template.cores,
        cpu_freq=template.cpu_freq,
        gpu_cores=template.gpu_cores,
        cuda=template.cuda,
        gpu_freq=template.gpu_freq,
        ram_mem=template.ram_mem,
        ram_freq=template.ram_freq,
        memory=template.memory
    )
    db.session.add(conf)
    db.session.commit()

    vm = VM(
        os=template.os,
        description=template.description,
        photo=template.photo,
        price=template.price,
        id_conf=conf.id,
        user_id=current_user.id,
        status='In Cart'
    )
    db.session.add(vm)
    db.session.commit()

    cart_item = Cart(user_id=current_user.id, vm_id=vm.id, quantity=1)
    db.session.add(cart_item)
    db.session.commit()

    flash('Виртуальная машина добавлена в корзину!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)

@bp.route('/cart/delete/<int:id>', methods=['POST'])
@login_required
def cart_delete(id):
    item = Cart.query.get_or_404(id)
    if item.user_id != current_user.id:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('user.cart'))
    db.session.delete(item)
    db.session.commit()
    flash('Удалено из корзины', 'info')
    return redirect(url_for('user.cart'))


@bp.route('/cart/pay/<int:id>', methods=['GET', 'POST'])
@login_required
def cart_pay(id):
    item = Cart.query.get_or_404(id)
    if request.method == 'POST':
        validate_form_fields(request.form)

        payment = Payment(
            user_id=current_user.id,
            vm_id=item.vm_id,
            amount=item.vm.price,
            payment_info=request.form['payment_info'],
            status='Paid'
        )
        db.session.add(payment)
        db.session.commit()

        # Вычисляем текущую дату и дату через месяц
        today = datetime.today()
        date_start = today.strftime('%Y-%m-%d')
        date_finish = (today + relativedelta(months=1)).strftime('%Y-%m-%d')

        deal = Deal(
            user_id=current_user.id,
            vm_id=item.vm_id,
            amount=item.vm.price,
            date_start=date_start,
            date_finish=date_finish
        )
        db.session.add(deal)
        db.session.commit()

        random_hex = secrets.token_hex(64)  # 512 бит
        fake_key = f"ssh-rsa {random_hex} generated@vmshop"
        ssh_key = SSHKey(user_id=current_user.id, vm_id=item.vm_id, key_content=fake_key)
        db.session.add(ssh_key)
        db.session.commit()

        db.session.delete(item)
        db.session.commit()

        flash('Оплата прошла. Машина активирована!', 'success')
        return redirect(url_for('user.my_vms'))

    return render_template('payment.html', item=item)


@bp.route('/my_vms')
@login_required
def my_vms():
    deals = Deal.query.filter_by(user_id=current_user.id).all()
    return render_template('my_vms.html', deals=deals)

@bp.route('/my_vms/ssh/<int:vm_id>')
@login_required
def download_ssh(vm_id):
    ssh_key = SSHKey.query.filter_by(vm_id=vm_id, user_id=current_user.id).first()
    if not ssh_key:
        flash('Ключ не найден', 'danger')
        return redirect(url_for('user.my_vms'))
    return send_file(io.BytesIO(ssh_key.key_content.encode()), as_attachment=True, download_name=f'ssh_key_{vm_id}.txt', mimetype='text/plain')

@bp.route('/my_vms/status/<int:vm_id>')
@login_required
def toggle_status(vm_id):
    vm = VM.query.get_or_404(vm_id)
    if vm.user_id != current_user.id:
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('user.my_vms'))
    vm.status = 'Running' if vm.status == 'Stopped' else 'Stopped'
    db.session.commit()
    flash(f'Статус изменен на {vm.status}', 'info')
    return redirect(url_for('user.my_vms'))
