from sqlalchemy import DateTime, ForeignKey, String, BigInteger, Column, BOOLEAN, Text, Integer
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date_time = Column(DateTime)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=True)
    user = relationship('User', backref='schedule')


class User(Base):
    __tablename__ = 'user'
    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    status = Column(BOOLEAN, nullable=False)


class Topic(Base):
    __tablename__ = 'topic'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    items = relationship("TopicItem", backref="topic", cascade="all, delete-orphan", lazy="selectin")


class TopicItem(Base):
    __tablename__ = 'topic_item'
    id = Column(Integer, primary_key=True, autoincrement=True, )
    topic_id = Column(BigInteger, ForeignKey('topic.id'), nullable=False)
    title = Column(String(100), nullable=False)
    text = Column(Text, nullable=False)


class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    high_score_message = Column(Text, nullable=False)
    medium_score_message = Column(Text, nullable=False)
    low_score_message = Column(Text, nullable=False)

    items = relationship("TestItem", backref="test", cascade="all, delete-orphan", lazy="selectin")


class TestItem(Base):
    __tablename__ = 'test_item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    test_id = Column(BigInteger, ForeignKey('test.id'), nullable=False)


class ActualActivity(Base):
    __tablename__ = 'actual_activity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    _topic_id = Column("topic_id", BigInteger, ForeignKey('topic.id'), nullable=True)
    _test_id = Column("test_id", BigInteger, ForeignKey('test.id'), nullable=True)

    topic = relationship("Topic", lazy="joined")
    test = relationship("Test", lazy="joined")

    @property
    def topic_id(self):
        return self._topic_id

    @topic_id.setter
    def topic_id(self, value):
        self._topic_id = value
        if value is not None:
            self._test_id = None

    @property
    def test_id(self):
        return self._test_id

    @test_id.setter
    def test_id(self, value):
        self._test_id = value
        if value is not None:
            self._topic_id = None
