function toggleContent(button) {
    let cardBody = button.parentElement;
    let postContent = cardBody.querySelector(".post-content");

    if (postContent.style.maxHeight) {
        postContent.style.maxHeight = null;
        button.textContent = "View less";
    } else {
        postContent.style.maxHeight = "745px"; // Set your desired max height here
        button.textContent = "View more";
    }
}

window.addEventListener('load', function () {
    let postContents = document.querySelectorAll('.post-content');

    postContents.forEach(function (postContent) {
        if (postContent.scrollHeight <= 745) {
            let moreButton = postContent.parentElement.querySelector(".more-button");
            moreButton.style.display = 'none';
        }
    });
});