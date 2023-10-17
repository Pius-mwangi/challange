from flask_sqlalchemy import SQLAlchemy
import marshmallow
from flask_login import LoginManager

def _include_sqlalchemy(obj, query_class=None):
    from sqlalchemy import orm
    query_class = obj.Query = orm.Query if query_class is None else query_class
    for module in 'engine url Model query session'.split():
        setattr(obj, module, getattr(orm, module))

# Add the method to the SQLAlchemy class
SQLAlchemy._include_sqlalchemy = _include_sqlalchemy

db = SQLAlchemy()
ma = marshmallow
login_manager = LoginManager()

def init_db(app):
    db.init_app(app)
