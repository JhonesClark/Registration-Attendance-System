from flask import Blueprint, render_template
from flask_login import login_required

from ..decorators import admin_required

ei_bp = Blueprint('export_import', __name__, url_prefix='/data', template_folder='../templates')


@ei_bp.route('/export')
@login_required
@admin_required
def export():
    return render_template('admin/export.html')


@ei_bp.route('/import')
@login_required
@admin_required
def import_view():
    return render_template('admin/import.html')
