function deletePostAndFiles(postId) {
    if (confirm("Confirm to delete this post?")) {
          fetch("/delete_post", {
            method: "POST",
            body: JSON.stringify({ postId: postId }),
          }).then((_res) => {
            location.reload();
          });
    }
}