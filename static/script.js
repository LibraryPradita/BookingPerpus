document.addEventListener("DOMContentLoaded", () => {
    const bookingForm = document.getElementById("booking-form");
    const ruanganInput = document.getElementById("ruangan");
    const tanggalInput = document.getElementById("tanggal");
    const jamContainer = document.getElementById("jam-container");
    const selectedJamInput = document.getElementById("jam");

    const jumlahOrangInput = document.getElementById("jumlah_orang");
    const durasiInput = document.getElementById("durasi");

    function createJamButton(waktu, available) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "btn m-1 jam-btn";
        button.textContent = waktu;

        if (available) {
            button.classList.add("btn-outline-success");
            button.disabled = false;
            button.addEventListener("click", () => {
                document.querySelectorAll(".jam-btn").forEach(btn => {
                    btn.classList.remove("active", "btn-success");
                    btn.classList.add("btn-outline-success");
                });

                button.classList.remove("btn-outline-success");
                button.classList.add("btn-success", "active");
                selectedJamInput.value = waktu;
            });
        } else {
            button.classList.add("btn-secondary", "unavailable");
            button.disabled = true;
        }

        return button;
    }

    async function fetchAvailableTimes() {
        const ruangan = ruanganInput.value;
        const tanggal = tanggalInput.value;

        jamContainer.innerHTML = "";
        selectedJamInput.value = "";

        if (!ruangan || !tanggal) return;

        try {
            const res = await fetch(`/get_available_times?ruangan=${encodeURIComponent(ruangan)}&tanggal=${encodeURIComponent(tanggal)}`);
            const result = await res.json();

            if (Array.isArray(result.jam)) {
                result.jam.forEach(({ waktu, available }) => {
                    jamContainer.appendChild(createJamButton(waktu, available));
                });
            }
        } catch (err) {
            console.error("❌ Gagal mengambil jam tersedia:", err);
        }
    }

    ruanganInput.addEventListener("change", fetchAvailableTimes);
    tanggalInput.addEventListener("change", fetchAvailableTimes);

    bookingForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const jumlah_orang = parseInt(jumlahOrangInput.value, 10);
        const durasi = parseInt(durasiInput.value, 10);

        const data = {
            nama: document.getElementById("nama").value.trim(),
            nim: document.getElementById("nim").value.trim(),
            email: document.getElementById("email").value.trim(),
            ruangan: ruanganInput.value.trim(),
            tanggal: tanggalInput.value.trim(),
            jam: selectedJamInput.value.trim(),
            durasi,
            jumlah_orang
        };

        if (!data.nama || !data.nim || !data.email || !data.ruangan || !data.tanggal || !data.jam) {
            alert("⚠️ Harap lengkapi semua data.");
            return;
        }

        if (isNaN(jumlah_orang) || jumlah_orang <= 0 || isNaN(durasi) || durasi <= 0) {
            alert("⚠️ Jumlah orang dan durasi harus lebih dari 0.");
            return;
        }

        const submitBtn = bookingForm.querySelector("button[type='submit']");
        submitBtn.disabled = true;
        submitBtn.textContent = "Mengirim...";

        try {
            const res = await fetch("/booking", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            const result = await res.json();

            if (res.ok && result.success) {
                alert("✅ Booking berhasil!");
                bookingForm.reset();
                jamContainer.innerHTML = "";
                selectedJamInput.value = "";
            } else {
                alert("❌ " + (result.message || "Booking gagal."));
            }
        } catch (err) {
            alert("❌ Terjadi kesalahan saat mengirim booking.");
            console.error(err);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Booking Sekarang";
        }
    });

   // ✅ Admin actions: ACC, CANCEL, REJECT, DELETE
   document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", function () {
            const bookingId = this.dataset.id;
            if (!confirm("Apakah Anda yakin ingin menghapus booking ini?")) return;

            fetch("/update_booking", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ booking_id: bookingId, action: "DELETE" })
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    document.getElementById(`row-${bookingId}`).remove();
                } else {
                    alert(data.message || "Gagal menghapus booking.");
                }
            })
            .catch(err => {
                console.error("❌ Error:", err);
                alert("Gagal menghapus booking.");
            });
        });
    });
});
