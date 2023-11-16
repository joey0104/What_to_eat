from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from __init__ import engine


Base = declarative_base()

class Food(Base):
    __tablename__="Food"

    id = Column("id", Integer, primary_key=True)
    name=Column("name", String)
    direction = Column("direction", String)
    ingredient = Column("ingredient", String)

    def __init__(self, name, ingredient, direction):
      self.name=name
      self.ingredient=ingredient
      self.direction=direction

Base.metadata.create_all(bind=engine)