from models import User
from sqlalchemy.orm import scoped_session

class UserRepository:
    def __init__(self, db_session: scoped_session) -> None:
        self.db_session = db_session

    def add_user(self, user: User):
        self.db_session.add(user)
        self.db_session.commit()

    def get_all(self):
        return User.query.all()