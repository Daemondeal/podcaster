"use strict";

(function () {
    const searchInput = document.getElementById("searchInput");
    const searchTargets = document.querySelectorAll("[data-search-content]");

    searchInput.addEventListener("input", (e) => {
        const value = searchInput.value.toLowerCase();

        for (const target of searchTargets) {
            if (target.dataset.searchContent.toLowerCase().indexOf(value) === -1) {
                target.classList.add("search-hidden");
            } else {
                target.classList.remove("search-hidden");
            }
        }
    })
})();