import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# User table has the following columns
# id, name, email and picture
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# categories table has the following columns
# id, name
# foreign keys relationship with User table - user_id and user
# foreign key for category_item table - items
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    items = relationship('CategoryItem')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        category_items = [item.serialize for item in self.items]
        return{
            'name': self.name,
            'id': self.id,
            'Item': category_items,
        }


# category_items table has the following columns
# id, name, description
# foreign key relationship with User table - user_id and user
# foreign key for category table - category
class CategoryItem(Base):
    __tablename__ = 'category_items'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(5000))
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'cat_id': self.category_id,
        }


#engine = create_engine('sqlite:///catalog.db')
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.create_all(engine)
