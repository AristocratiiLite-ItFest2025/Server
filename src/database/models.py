from typing import Optional

from sqlalchemy import (VARCHAR, Boolean, Column, DateTime, Enum, Float,
                        ForeignKey, Integer, Table, Text, inspect)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import object_session, relationship
from sqlalchemy.sql import func, select
from sqlalchemy.sql.functions import count

from database import Base, get_db


class SerializableMixin:

    def to_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }


chat_participants = Table(
    'chat_participants', Base.metadata,
    Column('chat_id', Integer, ForeignKey('chats.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True))

event_attendees = Table(
    'event_attendees', Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True))


class User(Base, SerializableMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(255), unique=True, nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    bani_sold = Column(Float, default=0.0)
    isVerified = Column(Enum('NGO', 'SPONSOR', 'PERSON', name='user_type'),
                        nullable=False)
    isPublic = Column(Boolean, default=False)
    avatar_image = Column(VARCHAR(255))
    chat_id = Column(
        Integer, ForeignKey('chats.id'),
        nullable=True)  # Can be removed since we now have many-to-many

    chats = relationship('Chat',
                         secondary=chat_participants,
                         back_populates='participants')

    events = relationship('Event',
                          secondary=event_attendees,
                          back_populates='attendees')


class Event(Base, SerializableMixin):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    attendees = relationship('User',
                             secondary='event_attendees',
                             back_populates='events')

    @property
    def attendees_count(self):
        if self.attendees is None:
            return 0
        return len(self.attendees)

    def to_dict(self):
        data = super().to_dict()
        data["attendees_count"] = self.attendees_count
        data["attendees"] = [attendee.id for attendee in self.attendees]

        data["start_time"] = data["start_time"].isoformat()
        data["end_time"] = data["end_time"].isoformat()
        return data

    description = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email_for_contact = Column(VARCHAR(255), nullable=True)
    phone_contact = Column(VARCHAR(255), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    image = Column(VARCHAR(255))
    icon_image = Column(VARCHAR(255))
    recurring_duration = Column(VARCHAR(255))


class Chat(Base, SerializableMixin):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    last_message = Column(VARCHAR(255), nullable=True)
    name = Column(VARCHAR(255), nullable=False)
    chat_image = Column(VARCHAR(255))

    participants = relationship('User',
                                secondary=chat_participants,
                                back_populates='chats')


class Entry(Base, SerializableMixin):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    text = Column(Text, nullable=False)

    def to_dict(self):
        data = super().to_dict()
        data["timestamp"] = data["timestamp"].isoformat()
        return data
