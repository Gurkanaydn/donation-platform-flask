from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_caching import Cache
from flask_swagger_ui import get_swaggerui_blueprint
from flask_socketio import SocketIO
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv
import redis

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")
cache = Cache()
redis_client = None
load_dotenv()

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)  # Tüm route’lar için izin verir
    r_host = os.getenv("REDIS_HOST", "localhost")
    r_port = os.getenv("REDIS_PORT", 6379)

    app.config.from_object("app.config.Config")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=5)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    
    app.config.setdefault('CACHE_TYPE', 'RedisCache')
    app.config.setdefault('CACHE_REDIS_HOST', r_host)
    app.config.setdefault('CACHE_REDIS_PORT', r_port)
    app.config.setdefault('CACHE_DEFAULT_TIMEOUT', 300)
    cache.init_app(app)


    global redis_client
    redis_client = redis.StrictRedis(host=r_host, port=r_port, db=0, decode_responses=True)

    from app.routes.auth import auth_bp
    from app.routes.campaign import campaign_bp
    from app.routes.donation import donation_bp
    from app.routes.main import main_bp


    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(campaign_bp, url_prefix="/api/campaigns") 
    app.register_blueprint(donation_bp, url_prefix="/api/donation")
    app.register_blueprint(main_bp)


    SWAGGER_URL = '/docs'
    API_URL = '/static/swagger.yaml'
    swagger_ui = get_swaggerui_blueprint(SWAGGER_URL,API_URL)
    app.register_blueprint(swagger_ui, url_prefix=SWAGGER_URL)

    return app
