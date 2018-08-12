from base import Base
from sqlalchemy import Column, String, Boolean, Integer, DateTime, BigInteger
import datetime

class Network(Base):
    __tablename__ = 'networks'

    id = Column(Integer, primary_key=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    channel = Column(Integer)
    pan_id = Column(Integer)
    extended_pan_id = Column(String)
    nwk_key = Column(String)
