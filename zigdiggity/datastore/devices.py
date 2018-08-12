from base import Base
from sqlalchemy import Column, String, Boolean, Integer, DateTime, BigInteger
import datetime

# Stack Overflow, yo
to_hex = lambda x:"".join([hex(ord(c))[2:].zfill(2) for c in x])

class Device(Base):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    channel = Column(Integer)
    pan_id = Column(Integer)
    address = Column(Integer)
    extended_pan_id = Column(String) 
    extended_address = Column(String)
    is_coordinator = Column(Boolean)

    d15d4_sequence_number = Column(Integer) # Technically between 0 and 255, but int should work
    nwk_sequence_number = Column(Integer)
    aps_counter = Column(Integer)
    zcl_sequence_number = Column(Integer)
    frame_counter = Column(Integer)

    def __repr__(self):
        pan_str = "0x%x"%self.pan_id if not self.pan_id is None else None
        addr_str = "0x%x"%self.address if not self.address is None else None
        epan_str = "0x%x"%long(self.extended_pan_id) if not self.extended_pan_id is None else None
        eaddr_str = "0x%x"%long(self.extended_address) if not self.extended_address is None else None
        return "<Device(channel=%s, pan_id=%s, address=%s, extended_pan_id=%s, extended_address=%s, coordinator=%s, last_update=%s)>"%(self.channel, pan_str, addr_str, epan_str, eaddr_str, self.is_coordinator, self.last_updated)
