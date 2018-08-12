from base import Base
from sqlalchemy import Column, Integer, String, Boolean

class Radio(Base):
    __tablename__='radios'

    id = Column(Integer, primary_key=True)
    radio_type = Column(String)
    device_string = Column(String)
    was_listener = Column(Boolean)

    def __repr__(self):
        role = "listener" if self.was_listener else "sender"
        return "<Radio(DEV=%s, TYPE=%s, ROLE=%S)>" % (self.device_string, self.radio_type, self.role)
