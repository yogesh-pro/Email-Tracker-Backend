
from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import mongo, bcrypt, jwt, limiter

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    mongo.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app)  # Enable CORS for all routes by default

    # Register blueprints (routes)
    from .routes.auth import auth_bp
    from .routes.tracker import tracker_bp
    from .routes.pixel import pixel_bp
    from .routes.analytics import analytics_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tracker_bp, url_prefix='/api/tracker')
    app.register_blueprint(pixel_bp, url_prefix='/api/pixel')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    @app.route('/')
    def index():
        return {"message": "Email Tracker API is running"}

    return app
