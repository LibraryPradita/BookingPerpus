document.addEventListener("DOMContentLoaded", function () {
    const jamContainer = document.getElementById("jam-container");
    const selectedJamInput = document.getElementById("selected-jam");
    const bookingForm = document.querySelector("form");
    const tanggalInput = document.getElementById("tanggal");
    const ruanganInput = document.getElementById("ruangan");

    function loadAvailableTimes() {
        let tanggal = tanggalInput.value;
        let ruangan = ruanganInput.value;

        if (!ruangan || !tanggal) return;

        jamContainer.innerHTML = '<p class="text-center">Memuat slot jam...</p>';

        fetch(`/get_available_times?ruangan=${ruangan}&tanggal=${tanggal}`)
            .then(response => response.json())
            .then(data => {
                jamContainer.innerHTML = "";

                if (!data.jam.length) {
                    jamContainer.innerHTML = '<p class="text-danger text-center">Tidak ada slot tersedia.</p>';
                    return;
                }

                jamContainer.style.display = "grid";
                jamContainer.style.gridTemplateColumns = "repeat(auto-fill, minmax(80px, 1fr))";
                jamContainer.style.gap = "10px";
                jamContainer.style.justifyContent = "center";

                data.jam.forEach(({ waktu, available }) => {
                    let button = document.createElement("button");
                    button.className = `btn ${available ? "btn-success" : "btn-secondary"}`;
                    button.innerText = waktu.padStart(5, "0");
                    button.disabled = !available;
                    Object.assign(button.style, {
                        padding: "12px",
                        fontSize: "14px",
                        textAlign: "center",
                        borderRadius: "10px",
                        minWidth: "80px"
                    });

                    button.addEventListener("click", function (event) {
                        event.preventDefault();
                        document.querySelectorAll("#jam-container button").forEach(btn => {
                            btn.classList.remove("btn-primary");
                            btn.style.border = "none";
                        });
                        button.classList.add("btn-primary");
                        button.style.border = "3px solid #fff";
                        selectedJamInput.value = waktu;
                    });

                    jamContainer.appendChild(button);
                });
            })
            .catch(error => {
                console.error("Error:", error);
                jamContainer.innerHTML = '<p class="text-danger text-center">Gagal memuat data.</p>';
            });
    }

    bookingForm.addEventListener("submit", function (event) {
        event.preventDefault();

        if (!selectedJamInput.value) {
            alert("Pilih jam terlebih dahulu sebelum booking!");
            return;
        }

        let formData = new FormData(bookingForm);

        fetch("/booking", { method: "POST", body: formData })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showPopup(data.message);
                    resetForm();
                    loadAvailableTimes();  // Reload pilihan jam setelah reset
                }
            })
            .catch(error => console.error("Error:", error));
    });

    function showPopup(message) {
        let popup = document.createElement("div");
        Object.assign(popup.style, {
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            background: "rgba(0,0,0,0.8)",
            color: "white",
            padding: "15px 30px",
            borderRadius: "5px",
            zIndex: "1000",
            textAlign: "center"
        });
        popup.innerText = message;
        document.body.appendChild(popup);
        setTimeout(() => popup.remove(), 5000);
    }

    function resetForm() {
        bookingForm.reset();  
        selectedJamInput.value = "";  
        jamContainer.innerHTML = "";  
    }

    [ruanganInput, tanggalInput].forEach(input => input.addEventListener("change", loadAvailableTimes));
});
