from datetime import datetime

from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.sql.functions import now

from common.variables import SERVER_DB_URL


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(unique=True)
    last_login: Mapped[datetime | None] = None

    def __str__(self):
        return self.name


class ActiveUsers(Base):
    __tablename__ = "active_users"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    ip: Mapped[str]
    port: Mapped[int]
    login_time: Mapped[datetime] = mapped_column(default=now())


class LoginHistory(Base):
    __tablename__ = "login_history"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    ip: Mapped[str]
    port: Mapped[int]
    date_time: Mapped[datetime] = mapped_column(default=now())


class ServerDatabase:
    def __init__(self, db_url: str):
        self.engine = create_engine(url=db_url, echo=False)
        self.session_factory = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def create_all(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def clear_active_users(self) -> None:
        with self.session_factory() as session:
            session.query(ActiveUsers).delete()
            session.commit()

    def user_login(self, username: str, ip_address: str, port: int) -> User:
        with self.session_factory() as session:
            stmt = select(User).where(User.name == username)
            user = session.scalar(stmt)

            if not user:
                user = User(name=username)
                session.add(user)

            user.last_login = now()
            session.commit()

            active_user = ActiveUsers(user_id=user.id, ip=ip_address, port=port)
            session.add(active_user)

            history = LoginHistory(user_id=user.id, ip=ip_address, port=port)
            session.add(history)

            session.commit()

            return user

    def user_logout(self, username: str) -> None:
        with self.session_factory() as session:
            stmt = select(User.id).where(User.name == username)
            user_id = session.scalar(stmt)

            stmt = select(ActiveUsers).where(ActiveUsers.user_id == user_id)
            active_user = session.scalar(stmt)
            session.delete(active_user)

            session.commit()


if __name__ == "__main__":
    server_db = ServerDatabase(db_url=SERVER_DB_URL)
    server_db.create_all()

    server_db.clear_active_users()

    user = server_db.user_login(username="us", ip_address="123.123.123.123", port=123123)
    server_db.user_logout(username=user.name)
