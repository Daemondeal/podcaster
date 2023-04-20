"use strict";

(function () {
    const forms = document.querySelectorAll(".needs-validation");

    for (const form of forms) {
        form.addEventListener('submit', event => {
            let atLeastOneInvalidTextarea = false;

            // Il tag <textarea> in HTML non supporta la validazione 
            // tramite pattern, quindi la implemento manualmente
            const textareas = form.querySelectorAll("textarea[pattern]");
            for (const textarea of textareas) {
                console.log(textarea.attributes);

                const pattern = textarea.attributes.pattern.value;
                const regex = new RegExp(`^${pattern}$`);

                if (!regex.test(textarea.value)) {
                    atLeastOneInvalidTextarea = true;

                    // Qualsiasi stringa eccetto la stringa vuota rende l'input invalido
                    textarea.setCustomValidity("invalid");
                } else {
                    // Impostare customValidity come stringa vuota rende l'input valido
                    textarea.setCustomValidity("");
                }
            }

            if (!form.checkValidity() || atLeastOneInvalidTextarea) {
                event.preventDefault();
                event.stopPropagation();
            }

            form.classList.add("was-validated");
        }, false);
    }
})();
