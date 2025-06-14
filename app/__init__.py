from flask import Flask
from app.config import Config

# db = SQLAlchemy()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Blueprints
    from app.routes.routes_incidente import incidente_bp
    # from app.routes.routes_asistencia import asistencia_bp
    # from app.routes.routes_justificacion import justificacion_bp
    from app.routes.routes_encuesta import encuesta_bp
    
    app.register_blueprint(incidente_bp)
    # app.register_blueprint(asistencia_bp)
    # app.register_blueprint(justificacion_bp)
    app.register_blueprint(encuesta_bp)

    return app