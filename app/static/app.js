const urlInput = document.getElementById("url-input");
const shortenBtn = document.getElementById("shorten-btn");
const resultCard = document.getElementById("result-card");
const shortUrl = document.getElementById("short-url");
const originalUrl = document.getElementById("original-url");
const copyBtn = document.getElementById("copy-btn");
const refreshBtn = document.getElementById("refresh-btn");
const errorMessage = document.getElementById("error-message");
const clickCount = document.getElementById("click-count");
const statsLink = document.getElementById("stats-link");

const trackerInput = document.getElementById("tracker-input");
const trackBtn = document.getElementById("track-btn");
const trackerError = document.getElementById("tracker-error");
const trackerResult = document.getElementById("tracker-result");
const trackerClickCount = document.getElementById("tracker-click-count");
const trackerShortLink = document.getElementById("tracker-short-link");
const trackerOriginalUrl = document.getElementById("tracker-original-url");


shortenBtn.addEventListener("click", shortenUrl);

urlInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        shortenUrl();
    }
});


async function shortenUrl() {
    const url = urlInput.value.trim();

    errorMessage.textContent = "";
    resultCard.classList.add("hidden");

    if (!url) {
        errorMessage.textContent = "Please enter a URL.";
        return;
    }

    shortenBtn.disabled = true;
    shortenBtn.innerHTML = "Creating...";

    try {
        const response = await fetch("/links", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                original_url: url
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to shorten this URL."
            );
        }

        const generatedUrl =
            `${window.location.origin}/${data.short_code}`;

        shortUrl.textContent = generatedUrl;
        shortUrl.href = generatedUrl;

        originalUrl.textContent = data.original_url;

        statsLink.href =
            `/links/${data.short_code}/stats`;

        try {
            const statsResponse = await fetch(
                `/links/${data.short_code}/stats`
            );

            if (statsResponse.ok) {
                const stats = await statsResponse.json();
                clickCount.textContent = stats.click_count;
            } else {
                clickCount.textContent = "0";
            }
        } catch {
            clickCount.textContent = "0";
        }

        resultCard.classList.remove("hidden");

    } catch (error) {
        errorMessage.textContent = error.message;
    }

    shortenBtn.disabled = false;
    shortenBtn.innerHTML = 'Shorten URL <span>→</span>';
}


refreshBtn.addEventListener("click", refreshAnalytics);


async function refreshAnalytics() {
    const url = shortUrl.textContent;

    if (!url) {
        return;
    }

    refreshBtn.disabled = true;
    refreshBtn.textContent = "Refreshing...";

    try {
        const parsedUrl = new URL(url);
        const shortCode = parsedUrl.pathname.replace(/^\/+|\/+$/g, "");

        const response = await fetch(
            `/links/${encodeURIComponent(shortCode)}/stats`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to refresh analytics."
            );
        }

        clickCount.textContent = data.click_count;

    } catch (error) {
        errorMessage.textContent = error.message;
    }

    refreshBtn.disabled = false;
    refreshBtn.textContent = "Refresh";
}


setInterval(() => {
    if (!resultCard.classList.contains("hidden")) {
        refreshAnalytics();
    }
}, 5000);


copyBtn.addEventListener("click", async () => {
    const url = shortUrl.textContent;

    if (!url) {
        return;
    }

    await navigator.clipboard.writeText(url);

    copyBtn.textContent = "Copied!";

    setTimeout(() => {
        copyBtn.textContent = "Copy";
    }, 1500);
});


trackBtn.addEventListener("click", trackExistingLink);

trackerInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        trackExistingLink();
    }
});


async function trackExistingLink() {
    const input = trackerInput.value.trim();

    trackerError.textContent = "";
    trackerResult.classList.add("hidden");

    if (!input) {
        trackerError.textContent = "Please enter a short URL.";
        return;
    }

    let shortCode = input;

    try {
        const parsedUrl = new URL(input);
        shortCode = parsedUrl.pathname.replace(/^\/+|\/+$/g, "");
    } catch {
        // Input is already a short code.
    }

    if (!shortCode) {
        trackerError.textContent = "Invalid short URL.";
        return;
    }

    trackBtn.disabled = true;
    trackBtn.innerHTML = "Checking...";

    try {
        const response = await fetch(
            `/links/${encodeURIComponent(shortCode)}/stats`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to find this short link."
            );
        }

        const generatedUrl =
            `${window.location.origin}/${data.short_code}`;

        trackerClickCount.textContent = data.click_count;

        trackerShortLink.textContent = generatedUrl;
        trackerShortLink.href = generatedUrl;

        trackerOriginalUrl.textContent = data.original_url;

        trackerResult.classList.remove("hidden");

    } catch (error) {
        trackerError.textContent = error.message;
    }

    trackBtn.disabled = false;
    trackBtn.innerHTML = 'Check analytics <span>→</span>';
}
