from flask import Blueprint, render_template

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/mi-perfil')
def perfil():
    return render_template('perfil.html')
