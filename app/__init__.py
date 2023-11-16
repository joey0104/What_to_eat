from sqlalchemy import create_engine

engine = create_engine("sqlite:///food.db", echo=True)

from flask import Flask
app=Flask(__name__)

from app import view
from app import run