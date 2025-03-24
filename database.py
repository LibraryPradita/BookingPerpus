from sqlalchemy import create_engine, Column, Integer, String, Date, Enum, CheckConstraint, text
from sqlalchemy.orm import declarative_base, sessionmaker
import enum
import contextlib

DATABASE_URL = "sqlite:///./booking.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@contextlib.contextmanager
def get_db():
    """Membuat session baru untuk setiap permintaan ke database."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookingStatus(str, enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    REJECTED = "Rejected"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, index=True, nullable=False)
    nim = Column(String, index=True, nullable=False)
    email = Column(String, index=True, nullable=False)
    ruangan = Column(String, index=True, nullable=False)
    tanggal = Column(Date, index=True, nullable=False)
    jam = Column(String, index=True, nullable=False)
    jumlah_orang = Column(Integer, CheckConstraint("jumlah_orang > 0"), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)

    def __repr__(self):
        return f"<Booking(id={self.id}, nama={self.nama}, tanggal={self.tanggal}, jam={self.jam}, status={self.status}, jumlah_orang={self.jumlah_orang})>"

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

# ✅ Memastikan skema database diperbarui tanpa menghapus data
def update_database():
    with engine.connect() as conn:
        existing_columns = conn.execute(text("PRAGMA table_info(bookings)")).fetchall()
        column_names = {col[1] for col in existing_columns}

        if "jumlah_orang" not in column_names:
            print("⚠️ Menambahkan kolom 'jumlah_orang' ke tabel bookings...")
            conn.execute(text("ALTER TABLE bookings ADD COLUMN jumlah_orang INTEGER"))
            conn.commit()

        if "status" not in column_names:
            print("⚠️ Menambahkan kolom 'status' ke tabel bookings...")
            conn.execute(text("ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT 'Pending'"))
            conn.commit()

    with get_db() as db:
        db.query(Booking).filter(Booking.status == "Rejected").update({"status": BookingStatus.REJECTED})
        db.commit()
        print("✅ Database diperbarui dengan status 'Rejected'!")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    update_database()
    print("✅ Database dan tabel berhasil dibuat atau diperbarui.")
