from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from database import Base

class EventLog(Base):
    __tablename__ = 's_event_logs'

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    device_serial = Column(String(100))
    event_time = Column(DateTime)
    camera_position = Column(String(50))
    detected_objects = Column(Text)  # JSON字串
    alert_level = Column(Integer)
    image_path = Column(String(255))
    video_path = Column(String(255))
    uploaded = Column(Boolean, default=False)
