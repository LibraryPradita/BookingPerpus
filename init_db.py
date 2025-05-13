from database import Base, engine, update_database

def init_database():
    try:
        # Membuat tabel dari semua model
        Base.metadata.create_all(bind=engine)
        print("✅ Tabel-tabel database berhasil dibuat!")

        # Menjalankan proses update kolom jika perlu
        update_database()
        print("✅ Proses update database selesai!")
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat inisialisasi database: {e}")

if __name__ == "__main__":
    init_database()
