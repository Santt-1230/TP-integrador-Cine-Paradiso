from flask import render_template

@app.route('/locales', methods = ['GET'])
def mostrar_locales():
    locales = [
        {'id_local':1, 'nombre': 'Cine Centro', 'direccion':''},
        {'id_local':2, 'nombre': 'Cine Norte', 'direccion':''},
        {'id_local':3, 'nombre': 'Cine Sur', 'direccion':''}
    ]
    return render_template('locales.html', locales=locales)