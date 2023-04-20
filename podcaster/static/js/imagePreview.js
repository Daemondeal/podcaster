"use strict";

(function () {
    const imagePreviewSource = document.querySelector("#imagePreviewSource");
    const imagePreviewTarget = document.querySelector("#imagePreviewTarget");
    const imagePlaceholder = document.querySelector("#imagePlaceholder");

    imagePreviewSource.addEventListener('change', (e) => applyFile());

    function applyFile() {
        const [file] = imagePreviewSource.files;
        if (file) {
            if (!imagePlaceholder.classList.contains("d-none")) {
                imagePlaceholder.classList.add("d-none");
                imagePreviewTarget.classList.remove("d-none");
            }
            imagePreviewTarget.src = URL.createObjectURL(file);
        }
    }

    applyFile();
})();