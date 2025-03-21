from sqlalchemy import Column, Integer, String, Date, Enum, CheckConstraint
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class BookingStatus(str, enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, index=True, nullable=False)
    nim = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    ruangan = Column(String, index=True, nullable=False)
    tanggal = Column(Date, index=True, nullable=False)  # Pastikan tanggal bertipe Date
    jam = Column(String, index=True, nullable=False)  # Tetap pakai String untuk jam
    durasi = Column(Integer, CheckConstraint("durasi > 0"), nullable=False)  # Minimal 1 jam
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)

    def __repr__(self):
        return f"<Booking(id={self.id}, nama={self.nama}, ruangan={self.ruangan}, tanggal={self.tanggal}, jam={self.jam}, status={self.status})>"
