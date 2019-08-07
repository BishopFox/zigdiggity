from base import Base
from sqlalchemy import Column, Binary, Boolean, Integer, DateTime, BigInteger
import datetime

class PAN(Base):
    __tablename__ = 'pan'

    id = Column(Integer, primary_key=True)

    network_id = Column(Integer, ForeignKey('network.id'))
    network = relationship("PAN", back_populates="pans")

    channel = Column(Integer)
    pan_id = Column(Binary)