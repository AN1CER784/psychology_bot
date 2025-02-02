

from sqlalchemy import DateTime, ForeignKey, String, BigInteger, Column, BOOLEAN, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Schedule(Base):
    __tablename__ = 'schedule'
    date_time = Column(DateTime, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=True)
    user = relationship('User', backref='schedule')


class User(Base):
    __tablename__ = 'user'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    status = Column(BOOLEAN, nullable=False)


class Content(Base):
    __tablename__ = 'content'
    title = Column(String(100), primary_key=True)


class ContentMessage(Base):
    __tablename__ = 'content_message'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    content_title = Column(String(100), ForeignKey('content.title'), nullable=False)
    content = relationship('Content', backref='content_message')
