"use strict";

(function () {
    const forms = document.querySelectorAll("form");

    for (const form of forms) {
        const fileReplacers = form.querySelectorAll(".file-replacer");

        for (const fileReplacer of fileReplacers) {
            const inputContainer = fileReplacer.querySelector(".file-replacer-input-container");
            const previousFile = fileReplacer.querySelector(".file-replacer-previous-file");
            const replacerButton = fileReplacer.querySelector(".file-replacer-delete-button");

            form.addEventListener("reset", (e) => {
                previousFile.classList.remove("d-none");
                inputContainer.classList.add("d-none");
            });

            replacerButton.addEventListener("click", (e) => {
                previousFile.classList.add("d-none");
                inputContainer.classList.remove("d-none");
            })
        }
    }

})();