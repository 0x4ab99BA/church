document.addEventListener('DOMContentLoaded', function() {

    const outerContainer = document.querySelector('.outer-container');

    outerContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('reply-button')) {
            const commentDiv = event.target.parentNode;
            const replyForm = commentDiv.querySelector('.reply-form');

            if (replyForm.style.display === 'none') {
                replyForm.style.display = 'block';
            } else {
                replyForm.style.display = 'none';
            }
        }
    });

    outerContainer.addEventListener('click', function(event) {
        if (event.target.classList.contains('submit-button')) {
            event.preventDefault();

            const form = event.target.closest('form');
            const formData = new FormData(form);

            fetch('/submit_comment', {
                method: 'POST',
                body: formData
            })
            .then(response => response.text())
            .then(html => {
                const commentContainer = document.querySelector('.outer-container');
                commentContainer.innerHTML = html;
            })
            .catch(error => console.error('Error:', error));
        }
    });
});