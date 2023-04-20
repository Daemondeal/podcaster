"use strict";

(function () {
    const modals = document.querySelectorAll(".modal");

    for (const modal of modals) {
        const forms = modal.querySelectorAll("form");
        console.log(forms);

        if (forms.length > 0) {
            modal.addEventListener("hidden.bs.modal", (e) => {
                for (const form of forms) {
                    form.reset();
                }
            });
        }
    }

})();