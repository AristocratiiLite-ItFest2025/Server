from sqlalchemy import VARCHAR, Column, Integer, Float, Boolean, ForeignKey, Text, DateTime

from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(255), unique=True, nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    bani_sold = Column(Float, default=0.0)
    isVerifiedNGO = Column(Boolean, default=False)
    isVerifiedSponsor = Column(Boolean, default=False)
    isVerifiedPerson = Column(Boolean, default=False)
    isPublic = Column(Boolean, default=False)
    avatar_image = Column(VARCHAR(255))
    chat_id = Column(Integer, ForeignKey('chats.id'))


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    short_description = Column(Text, nullable=False)
    attendees = Column(VARCHAR(255))  # This should be a relationship in a real-world scenario
    long_description = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email_for_contact = Column(VARCHAR(255))
    phone_contact = Column(VARCHAR(255))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    image = Column(VARCHAR(255))
    icon_image = Column(VARCHAR(255))
    recurring_duration = Column(VARCHAR(255))  # This should be handled with a library for recurrence

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    last_message_timestamp = Column(DateTime)
    last_message = Column(Text)
    name = Column(VARCHAR(255), nullable=False)
    chat_image = Column(VARCHAR(255))


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    text = Column(Text, nullable=False)

