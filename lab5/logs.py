from flask import Blueprint, render_template, request, current_app, send_file, flash, redirect, url_for
from flask_login import current_user, login_required
from lab5.auth import check_rights
from io import StringIO
import csv
from lab5.models import VisitLog, User
from lab5.extensions import db

logs_bp = Blueprint('logs', __name__, template_folder='templates/logs')


def log_visit():
    log = VisitLog(
        path=request.path,
        user_id=current_user.id if current_user.is_authenticated else None
    )
    db.session.add(log)
    db.session.commit()

@logs_bp.route('/')
@login_required
@check_rights(['Administrator', 'User'])
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    query = VisitLog.query.order_by(VisitLog.created_at.desc())
    if current_user.role == 'User':
        query = query.filter(VisitLog.user_id == current_user.id)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('logs/index.html', pagination=pagination)


from flask import send_file
import io
import csv

@logs_bp.route('/logs/by-pages')
@login_required
@check_rights(['Administrator'])
def pages_report():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Страница', 'Количество посещений'])
    visits = db.session.query(VisitLog.path, db.func.count(VisitLog.id)).group_by(VisitLog.path).all()
    for path, count in visits:
        writer.writerow([path, count])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='report.csv'
    )

@logs_bp.route('/logs/by-users')
@login_required
@check_rights(['Administrator'])
def users_report():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Пользователь', 'Количество посещений'])
    visits = db.session.query(User, db.func.count(VisitLog.id))\
        .outerjoin(VisitLog, VisitLog.user_id == User.id)\
        .group_by(User.id).all()

    for user, count in visits:
        full_name = f"{user.last_name} {user.first_name} {user.patronymic}" if user else 'Неаутентифицированный пользователь'
        writer.writerow([full_name, count])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='users_report.csv'
    )

    return render_template('logs/users_report.html', report=report)
