from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/fintech')
connection = engine.connect()

def get_connection():
    return connection

def get_dbengine():
    return engine

def get_session():
    Session = sessionmaker(bind=engine)
    return Session()