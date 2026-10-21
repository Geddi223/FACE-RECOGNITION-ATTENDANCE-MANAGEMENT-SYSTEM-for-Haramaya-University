document.addEventListener("DOMContentLoaded", function () {
    const loadingScreen = document.getElementById("loading");

    // Show loading before navigating to a new page
    document.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", function (event) {
            if (this.href.includes(window.location.origin)) {
                event.preventDefault();
                loadingScreen.classList.remove("hidden");
                setTimeout(() => {
                    window.location.href = this.href;
                }, 500); // Adjust delay if needed
            }
        });
    });

    // Hide loading when the page fully loads
    window.addEventListener("load", function () {
        loadingScreen.classList.add("hidden");
    });
});
