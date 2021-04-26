import datetime
import sqlalchemy
import random
from .db_session import SqlAlchemyBase
import hashlib
from data.user_sessions import UserSession
from data.friendships import Friendship


def calc_hash(password):
    return hashlib.md5(password.encode()).hexdigest()


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    updated_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    cell = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True,
                             default="fewfeewf", nullable=True)

    def friends(self, db_sess):
        """
        список друзей
        """
        friends = list(db_sess.query(Friendship).filter((Friendship.user_1_id == self.id)))
        return friends

    def __str__(self):
        return f"{self.cell} - {self.id}"

    @classmethod
    def find_by_id(cls, _user_id, db_sess):
        res = None
        found_users = list(db_sess.query(User).filter((User.id == _user_id)))
        if len(found_users) > 0:
            res = found_users[0]
        return res

    @classmethod
    def authenticate_user(cls, _user_login, _user_pass_hash, db_sess):
        print("Searching for user")
        found_users = db_sess.query(User).filter((User.cell == _user_login),
                                                 User.password == calc_hash(_user_pass_hash))
        found = []
        for i in found_users:
            found.append(i)
            print(i)

        if len(found) == 0:
            return [None, None]
        else:
            new_user_session = UserSession()
            new_user_session.user_id = found[0].id
            new_user_session.value = f"{random.random()}{random.random()}"
            db_sess.add(new_user_session)
            db_sess.commit()
            return [found[0], new_user_session]

    @classmethod
    def create(cls, _cell, _password, db_sess):
        new_user = User()
        new_user.cell = _cell
        new_user.password = calc_hash(_password)
        db_sess.add(new_user)
        db_sess.commit()

        new_user_session = UserSession()
        new_user_session.user_id = new_user.id
        new_user_session.value = f"{random.random()}{random.random()}"
        db_sess.add(new_user_session)
        db_sess.commit()
        return [new_user, new_user_session]

    @classmethod
    def check_session(cls, _secret):
        for user in User.users:
            for session_secret in user.session_secrets:
                if _secret == session_secret:
                    return user
        return None

    @classmethod
    def check_cookies(cls, cookies, db_sess):
        found_sessions = list(db_sess.query(UserSession).filter((UserSession.value == cookies.get("user_secret"))))
        if len(found_sessions):
            found_session = list(found_sessions)[0]
            user = list(db_sess.query(User).filter((User.id == found_session.user_id)))[0]
            return user
        else:
            return None

    @classmethod
    def all(cls, db_sess):
        all_users = db_sess.query(User).filter(User.id > 0)
        found = []
        for i in all_users:
            found.append(i)
        return found

    @classmethod
    def friendship_asker(cls, friendship, db_sess):
        res = None
        found = list(db_sess.query(User).filter((User.id == friendship.user_1_id)))
        if len(found) > 0:
            res = found[0]
        return res

    @classmethod
    def friendship_asked(cls, friendship, db_sess):
        res = None
        found = list(db_sess.query(User).filter((User.id == friendship.user_2_id)))
        if len(found) > 0:
            res = found[0]
        return res
