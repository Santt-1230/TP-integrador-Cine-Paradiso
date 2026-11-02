from routes import admin_bp, estadisticas_bp








app.register_blueprint(admin_bp)
app.register_blueprint(estadisticas_bp)