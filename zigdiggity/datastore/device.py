
from base import Base
from sqlalchemy import Column, Binary, Boolean, Integer, DateTime, BigInteger
import datetime

class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    pan_id = Column(Integer, ForeignKey('pan.id'))
    pan = relationship("PAN")
    
    address = Column(Binary)
    extended_address = Column(Binary)
    is_coordinator = Column(Boolean)

    # keeping track of numbers
    d15d4_sequence_number = Column(Integer)
    nwk_sequence_number = Column(Integer)
    aps_counter = Column(Integer)
    zcl_sequence_number = Column(Integer)
    frame_counter = Column(Integer)
