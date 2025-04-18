from flask import Flask
from flask_cors import CORS

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1.quiz_routes import quiz_bp
from app.api.v1.auth_routes import auth_bp
from app.api.v1.user_routes import user_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    # Create Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config["SECRET_KEY"] = settings.FLASK_SECRET_KEY
    
    # Set up logging
    setup_logging()
    
    # Set up CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    app.register_blueprint(quiz_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    
    # Add a health check endpoint
    @app.route("/health")
    def health_check():
        return {"status": "ok"}
    
    return app