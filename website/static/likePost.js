
function likePost(postId) {
    fetch("/like_post", {
        method: "POST",
        body: JSON.stringify({ postId: postId }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update the like count using the received data
        const likeCountElement = document.getElementById(`like-count-${postId}`);
        if (likeCountElement) {
            likeCountElement.textContent = data.updatedLikeCount;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

