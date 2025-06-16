from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app import db
from app.models import ConfTemplate, Service, ServiceHasConfTemplate
from app.forms import ConfTemplateForm
from app.security import validate_form_fields
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Вы должны войти в систему", "warning")
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function



@bp.route('/create_template', methods=['GET', 'POST'])
@login_required
@admin_required
def create_template():
    form = ConfTemplateForm()
    if form.validate_on_submit():
        validate_form_fields(request.form)

        template = ConfTemplate(
            name=form.name.data,
            os=form.os.data,
            description=form.description.data,
            photo=form.photo.data,
            cores=form.cores.data,
            cpu_freq=form.cpu_freq.data,
            gpu_cores=form.gpu_cores.data,
            cuda=form.cuda.data,
            gpu_freq=form.gpu_freq.data,
            ram_mem=form.ram_mem.data,
            ram_freq=form.ram_freq.data,
            memory=form.memory.data,
            price=form.price.data,
            discount=form.discount.data
        )
        db.session.add(template)
        db.session.commit()

        service_names = request.form.getlist('services')
        for service_name in service_names:
            service_name = service_name.strip()
            if not service_name:
                continue
            service = Service.query.filter_by(service_name=service_name).first()
            if not service:
                service = Service(service_name=service_name)
                db.session.add(service)
                db.session.commit()
            link = ServiceHasConfTemplate(service_id=service.id, conf_template_id=template.id)
            db.session.add(link)
        db.session.commit()

        flash('Шаблон успешно создан!', 'success')
        return redirect(url_for('main.index'))

    return render_template('create_vm.html', form=form)


@bp.route('/edit_template', methods=['POST'])
@login_required
@admin_required
def edit_template():
    template_id = request.form.get('id')
    if not template_id or not template_id.isdigit():
        flash("Некорректный ID шаблона", "danger")
        return redirect(url_for('main.index'))

    template = ConfTemplate.query.get_or_404(int(template_id))

    template.name = request.form.get('name', '').strip()
    template.os = request.form.get('os', '').strip()
    template.description = request.form.get('description', '').strip()
    template.photo = request.form.get('photo', '').strip()

    try:
        template.cores = int(request.form.get('cores', 0))
        template.cpu_freq = float(request.form.get('cpu_freq', 0.0))
        template.gpu_cores = int(request.form.get('gpu_cores', 0))
        template.cuda = int(request.form.get('cuda', 0))
        template.gpu_freq = float(request.form.get('gpu_freq', 0.0))
        template.ram_mem = int(request.form.get('ram_mem', 0))
        template.ram_freq = int(request.form.get('ram_freq', 0))
        template.memory = int(request.form.get('memory', 0))
        template.price = int(request.form.get('price', 0))
        template.discount = int(request.form.get('discount', 0))
    except ValueError:
        flash("Некорректные числовые значения", "danger")
        return redirect(url_for('main.index'))

    if template.discount < 0 or template.discount > 100:
        flash("Скидка должна быть в пределах от 0 до 100", "danger")
        return redirect(url_for('main.index'))

    db.session.commit()
    flash('Шаблон успешно обновлён!', 'success')
    return redirect(url_for('main.index'))
