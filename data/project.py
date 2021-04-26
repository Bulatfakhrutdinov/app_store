import sqlalchemy
from flask_login import UserMixin

from .db_session import SqlAlchemyBase


class Project(SqlAlchemyBase, UserMixin):
    __tablename__ = 'project'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    project_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    size = sqlalchemy.Column(sqlalchemy.String, nullable=True)
