from base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import expanduser
import radios
import networks
import devices

home = expanduser("~")

engine = create_engine('sqlite:///%s/.zigdiggity.db'%home, connect_args={'check_same_thread':False})
database_session = sessionmaker(engine)()
Base.metadata.create_all(bind=engine)
