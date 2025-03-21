document.addEventListener("DOMContentLoaded", function () {
    const jamContainer = document.getElementById("jam-container");
    const selectedJamInput = document.getElementById("selected-jam");
    const bookingForm = document.querySelector("form");

    function loadAvailableTimes() {
        let tanggal = document.getElementById("tanggal").value;
        let ruangan = document.getElementById("ruangan").value;

        if (ruangan && tanggal) {
            fetch(`/get_available_times?ruangan=${ruangan}&tanggal=${tanggal}`)
                .then(response => response.json())
                .then(data => {
                    jamContainer.innerHTML = "";

                    if (data.jam.length === 0) {
                        jamContainer.innerHTML = '<p class="text-danger">Tidak ada slot tersedia.</p>';
                        return;
                    }

                    data.jam.forEach(item => {
                        let button = document.createElement("button");
                        button.className = `btn btn-sm m-1 ${item.available ? "btn-success" : "btn-secondary"}`;
                        button.innerText = item.waktu;
                        button.disabled = !item.available;

                        button.addEventListener("click", function (event) {
                            event.preventDefault();
                            document.querySelectorAll("#jam-container button").forEach(btn => btn.classList.remove("btn-primary"));
                            button.classList.add("btn-primary");
                            selectedJamInput.value = item.waktu;
                        });

                        jamContainer.appendChild(button);
                    });
                })
                .catch(error => console.error("Error:", error));
        }
    }

    bookingForm.addEventListener("submit", function (event) {
        if (!selectedJamInput.value) {
            event.preventDefault();
            alert("Pilih jam terlebih dahulu sebelum booking!");
            return;
        }

        event.preventDefault(); // Hentikan submit default untuk menangani fetch
        let formData = new FormData(bookingForm);
        
        fetch("/booking", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showPopup(data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    function showPopup(message) {
        let popup = document.createElement("div");
        popup.innerText = message;
        popup.style.position = "fixed";
        popup.style.top = "50%";
        popup.style.left = "50%";
        popup.style.transform = "translate(-50%, -50%)";
        popup.style.background = "rgba(0,0,0,0.8)";
        popup.style.color = "white";
        popup.style.padding = "15px 30px";
        popup.style.borderRadius = "5px";
        popup.style.zIndex = "1000";
        document.body.appendChild(popup);

        setTimeout(() => {
            popup.remove();
        }, 3000);
    }

    document.getElementById("ruangan").addEventListener("change", loadAvailableTimes);
    document.getElementById("tanggal").addEventListener("change", loadAvailableTimes);
});
