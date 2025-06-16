from flask import Blueprint, render_template, request
from app.models import ConfTemplate
from sqlalchemy import func

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    selected_oses = request.args.getlist('os')
    normalized_oses = [os.lower() for os in selected_oses]

    if normalized_oses:
        templates = ConfTemplate.query.filter(
            func.lower(ConfTemplate.os).in_(normalized_oses)
        ).all()
    else:
        templates = ConfTemplate.query.all()


    os_values = ConfTemplate.query.with_entities(ConfTemplate.os).all()
    unique_oses = {}
    for (os_name,) in os_values:
        lower = os_name.lower()
        if lower not in unique_oses:
            unique_oses[lower] = os_name

    return render_template(
        'index.html',
        templates=templates,
        all_oses=unique_oses.values(),
        selected_oses=selected_oses
    )
