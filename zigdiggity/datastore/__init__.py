from base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import expanduser
import radios
import networks
import devices
import utils

home = expanduser("~")
engine = create_engine('sqlite:///%s/.zigdiggity.db'%home, connect_args={'check_same_thread':False})
database_session = sessionmaker(engine)() # I only want to expose the session
Base.metadata.create_all(bind=engine)