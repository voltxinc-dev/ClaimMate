from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    from .routes import routes_bp
    from .auth import auth

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(routes_bp)

    return app
