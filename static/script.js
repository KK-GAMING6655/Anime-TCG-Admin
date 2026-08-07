document.addEventListener("DOMContentLoaded", () => {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const uploadTypeInput = document.getElementById("upload_type");
    const fileGroup = document.getElementById("fileGroup");
    const urlGroup = document.getElementById("urlGroup");
    
    const form = document.getElementById("addCardForm");
    const submitBtn = document.getElementById("submitBtn");
    const btnText = submitBtn.querySelector(".btn-text");
    const spinner = submitBtn.querySelector(".spinner");

    // Live Preview elements
    const nameInput = document.getElementById("name");
    const raritySelect = document.getElementById("rarity");
    const valueInput = document.getElementById("value");
    const imageFileInput = document.getElementById("image_file");
    const imageUrlInput = document.getElementById("image_url");

    const previewTitle = document.getElementById("previewTitle");
    const previewBadge = document.getElementById("previewBadge");
    const previewValue = document.getElementById("previewValue");
    const previewImg = document.getElementById("previewImg");
    const cardPreview = document.getElementById("cardPreview");

    const rarityColors = {
        "Common": "#95a5a6",
        "Uncommon": "#2ecc71",
        "Rare": "#3498db",
        "Epic": "#9b59b6",
        "Legendary": "#f1c40f",
        "Super Legendary": "#e74c3c"
    };

    // Toggle Image Input Mode
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const type = btn.getAttribute("data-type");
            uploadTypeInput.value = type;

            if (type === "file") {
                fileGroup.classList.remove("hidden");
                urlGroup.classList.add("hidden");
            } else {
                urlGroup.classList.remove("hidden");
                fileGroup.classList.add("hidden");
            }
        });
    });

    // Dynamic Preview Listeners
    nameInput.addEventListener("input", (e) => {
        previewTitle.textContent = e.target.value.trim() || "Card Name";
    });

    valueInput.addEventListener("input", (e) => {
        previewValue.textContent = e.target.value || "0";
    });

    raritySelect.addEventListener("change", (e) => {
        const rarity = e.target.value;
        previewBadge.textContent = rarity;
        const color = rarityColors[rarity] || "#3498db";
        previewBadge.style.backgroundColor = color;
        cardPreview.style.borderColor = color;
    });

    imageUrlInput.addEventListener("input", (e) => {
        if (uploadTypeInput.value === "url" && e.target.value) {
            previewImg.src = e.target.value;
        }
    });

    imageFileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                previewImg.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    // Form Submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        // UI Loading state
        submitBtn.disabled = true;
        btnText.classList.add("hidden");
        spinner.classList.remove("hidden");

        const formData = new FormData(form);

        try {
            const response = await fetch("/api/add-card", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                showToast(`✅ Card created! ID: ${data.card_id}`, "success");
                form.reset();
                // Reset Preview Defaults
                previewTitle.textContent = "Card Name";
                previewValue.textContent = "0";
                previewImg.src = "https://via.placeholder.com/300x400/12131C/505370?text=Card+Image";
            } else {
                showToast(`❌ ${data.error}`, "error");
            }
        } catch (err) {
            showToast("❌ Network or server error occurred.", "error");
        } finally {
            submitBtn.disabled = false;
            btnText.classList.remove("hidden");
            spinner.classList.add("hidden");
        }
    });

    function showToast(message, type) {
        const toast = document.getElementById("toast");
        toast.textContent = message;
        toast.style.borderColor = type === "success" ? "#2ecc71" : "#e74c3c";
        toast.classList.remove("hidden");
        setTimeout(() => toast.classList.add("hidden"), 4000);
    }
});

