from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta
import json

api = Api()
jwt = JWTManager()
db = SQLAlchemy()
