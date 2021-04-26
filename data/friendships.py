import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Friendship(SqlAlchemyBase):
    __tablename__ = 'friedships'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_1_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user_2_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    updated_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    @classmethod
    def create_friendship(cls, user_1, user_2, db_sess):
        search_1 = list(
            db_sess.query(Friendship).filter((Friendship.user_1_id == user_1.id) & (Friendship.user_2_id == user_2.id)))
        search_2 = list(
            db_sess.query(Friendship).filter((Friendship.user_1_id == user_2.id) & (Friendship.user_2_id == user_1.id)))
        if len(search_1) > 0 or len(search_2) > 0:
            print(search_1[0])
            return
        new_friendship = Friendship()
        new_friendship.user_1_id = user_1.id
        new_friendship.user_2_id = user_2.id
        new_friendship.status = "ожидает подтверждения"
        db_sess.add(new_friendship)
        db_sess.commit()
