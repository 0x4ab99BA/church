document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.querySelector('.submit-button');
    const commentInput = document.querySelector('.form-control');

    console.log('commentInput', commentInput)

    submitButton.addEventListener('click', function() {
        let commentContent = document.querySelector('.form-control').value;
        const postIdInput = document.querySelector('input[name="post_id"]');
        const postId = postIdInput.value;

        const formData = new FormData();
        formData.append('comment_body', commentContent);
        formData.append('post_id', postId);
        formData.append('parent_comment_id', '0'); // Assuming parent_comment_id is null by default

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
    });
});


