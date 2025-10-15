from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import BaseConfig

app = Flask(__name__)
app.config.from_object(BaseConfig)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from yacut import api_views, models, views