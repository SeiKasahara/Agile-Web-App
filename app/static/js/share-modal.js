document.addEventListener("DOMContentLoaded", () => {
    // Modal elements
    const shareBtn = document.getElementById("share-dashboard-btn");
    const modal = document.getElementById("share-modal");
    const closeBtn = document.getElementById("close-share-btn");
    const backBtn = document.getElementById("back-to-selection-btn");
    const generateBtn = document.getElementById("generate-share-btn");
    const sendEmailBtn = document.getElementById("send-email-btn");
    const copyBtn = document.getElementById("copy-share-btn");
    
    // Step containers
    const step1 = document.getElementById("share-step-1");
    const step2 = document.getElementById("share-step-2");
    
    // Share elements
    const urlInput = document.getElementById("share-url-input");
    const emailInput = document.getElementById("share-email");
    const twitterBtn = document.getElementById("twitter-share");
    const facebookBtn = document.getElementById("facebook-share");
    const linkedinBtn = document.getElementById("linkedin-share");

    // Open modal
    shareBtn.addEventListener("click", () => {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
        showStep1();
    });

    // Close modal
    closeBtn.addEventListener("click", () => {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
        resetModal();
    });

    // Close on backdrop click
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.add("hidden");
            modal.classList.remove("flex");
            resetModal();
        }
    });

    // Back button
    backBtn.addEventListener("click", () => {
        showStep1();
    });

    // Generate share link
    generateBtn.addEventListener("click", async () => {
        const selectedComponents = Array.from(document.querySelectorAll("input[name='share_components']:checked"))
            .map(cb => cb.value);

        if (selectedComponents.length === 0) {
            alert("Please select at least one component to share");
            return;
        }

        try {
            // Disable generate button and show loading state
            disableButton(generateBtn);
            generateBtn.textContent = "Generating...";

            const shareData = await generateShareData();
            const response = await fetch("/share/create", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    ...shareData,
                    components: selectedComponents
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `Status ${response.status}`);
            }
            
            setupShareOptions(data.url);
            showStep2();
        } catch (err) {
            console.error(err);
            alert(err.message || "Failed to generate share link. Please try again.");
        } finally {
            // Re-enable generate button and restore text
            enableButton(generateBtn);
            generateBtn.textContent = "Generate Share Link";
        }
    });

    // Send email
    sendEmailBtn.addEventListener("click", async () => {
        const email = emailInput.value.trim();
        if (!email) {
            alert("Please enter a valid email address");
            return;
        }

        try {
            const response = await fetch("/share/send-email", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email,
                    shareUrl: urlInput.value
                }),
            });

            if (!response.ok) throw new Error(`Status ${response.status}`);
            
            alert("Email sent successfully!");
            emailInput.value = "";
        } catch (err) {
            console.error(err);
            alert("Failed to send email. Please try again.");
        }
    });

    // Copy link
    copyBtn.addEventListener("click", () => {
        urlInput.select();
        document.execCommand("copy");
        copyBtn.textContent = "Copied!";
        setTimeout(() => {
            copyBtn.textContent = "Copy Link";
        }, 2000);
    });

    // Helper functions
    function showStep1() {
        step1.classList.remove("hidden");
        step2.classList.add("hidden");
    }

    function showStep2() {
        step1.classList.add("hidden");
        step2.classList.remove("hidden");
    }

    function resetModal() {
        showStep1();
        urlInput.value = "";
        emailInput.value = "";
        for (const cb of document.querySelectorAll("input[name='share_components']")) {
            cb.checked = true;
        }
    }

    async function generateShareData() {
        const fuel = document.getElementById("fuel_type_select").value;
        const loc = document.getElementById("location_select").value;
        const date = document.getElementById("date_select").value;
        const forecastChart = Chart.getChart("forecastChart");
        const forecastConfig = JSON.parse(JSON.stringify(forecastChart.config));

        const params = new URLSearchParams({
            fuel_type: fuel,
            location: loc,
            date: date,
        });
        const url = `/dashboard/data?${params}`;
        const res = await fetch(url);
        const data = await res.json();

        return {
            fuel,
            loc,
            date,
            forecastConfig,
            heatmapPoints: data.points
        };
    }

    function setupShareOptions(shareUrl) {
        urlInput.value = shareUrl;
        const encoded = encodeURIComponent(shareUrl);
        const text = encodeURIComponent("Check out my FuelPrice Dashboard!");
        
        twitterBtn.href = `https://twitter.com/intent/tweet?url=${encoded}&text=${text}`;
        facebookBtn.href = `https://www.facebook.com/sharer/sharer.php?u=${encoded}`;
        linkedinBtn.href = `https://www.linkedin.com/sharing/share-offsite/?url=${encoded}`;
    }
}); 