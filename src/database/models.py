from typing import Optional

from sqlalchemy import (VARCHAR, Boolean, Column, DateTime, Enum, Float,
                        ForeignKey, Integer, Table, Text, inspect)
from sqlalchemy.orm import relationship

from database import Base


class SerializableMixin:

    def to_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }


# Association table for many-to-many relationship
chat_participants = Table(
    'chat_participants', Base.metadata,
    Column('chat_id', Integer, ForeignKey('chats.id'), primary_key=True),
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

    # Relationship with chats
    chats = relationship('Chat',
                         secondary=chat_participants,
                         back_populates='participants')


class Event(Base, SerializableMixin):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    name = Column(VARCHAR(255), nullable=False)
    attendees = Column(
        Integer,
        default=1)  # This should be a relationship in a real-world scenario
    description = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    email_for_contact = Column(VARCHAR(255), nullable=True)
    phone_contact = Column(VARCHAR(255), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    image = Column(VARCHAR(255))
    icon_image = Column(VARCHAR(255))
    recurring_duration = Column(
        VARCHAR(255))  # This should be handled with a library for recurrence


class Chat(Base, SerializableMixin):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    last_message_id = Column(Integer, ForeignKey('entries.id'), nullable=True)
    last_message = relationship('Entry', foreign_keys=[last_message_id])
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
