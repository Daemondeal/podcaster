"use strict";

(function () {
    const editButtons = document.querySelectorAll(".edit-button");

    function createEditInputs(editUrl, commentId, commentContent) {
        return `
            <form action="${editUrl}" method="POST" class="needs-validation" novalidate>
                <input type="hidden" name="commentid" value="${commentId}">
                <textarea class="form-control mb-2" name="comment" minlength="3" maxlength="1000" required>${commentContent.trim()}</textarea>
                <div class="invalid-feedback">Il commento deve avere almeno 3 caratteri.</div>
                <button class="btn btn-primary" type="submit">Modifica</button>
                <button type="button" class="btn btn-secondary" id="revertEdit${commentId}">Annulla</button>
            </form>
        `;
    }

    for (const button of editButtons) {
        button.addEventListener("click", (e) => {
            const editUrl = button.dataset.commentEditUrl;
            const commentId = button.dataset.commentId;

            const description = document.querySelector(`#comment-${commentId}`);
            const commentContent = description.innerHTML;

            description.innerHTML = createEditInputs(editUrl, commentId, commentContent);

            const submitForm = description.querySelector("form");

            submitForm.addEventListener('submit', event => {
                if (!submitForm.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }

                submitForm.classList.add("was-validated");
            }, false);

            const revertButton = document.querySelector(`#revertEdit${commentId}`);
            revertButton.addEventListener("click", (e) => {
                const description = document.querySelector(`#comment-${commentId}`);
                description.innerHTML = commentContent;
            })
        })
    }
})();
