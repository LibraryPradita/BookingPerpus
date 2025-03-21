from sqlalchemy import create_engine, Column, Integer, String, Date, Enum, CheckConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
import enum
import contextlib
from datetime import datetime

DATABASE_URL = "sqlite:///./booking.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
    tanggal = Column(Date, index=True, nullable=False)  # Tetap menggunakan Date
    jam = Column(String, index=True, nullable=False)  # String "HH:MM"
    jumlah_orang = Column(Integer, CheckConstraint("jumlah_orang > 0"), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)

    def __repr__(self):
        return f"<Booking(id={self.id}, nama={self.nama}, tanggal={self.tanggal}, jam={self.jam}, status={self.status})>"

# Membuat tabel jika script ini dijalankan langsung
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Database dan tabel berhasil dibuat atau diperbarui.")

@contextlib.contextmanager
def get_db():
    """Membuat session baru untuk setiap permintaan ke database."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
