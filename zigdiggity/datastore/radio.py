from base import Base
from sqlalchemy import Column, Integer, String, Boolean

class Radio(Base):
    __tablename__='radio'

    id = Column(Integer, primary_key=True)
    radio_type = Column(String)
    device_string = Column(String)
