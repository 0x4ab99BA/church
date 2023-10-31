function deleteGroupAndPosts(groupId) {
    if (confirm("Confirm to delete this group and all the posts belong to it?")) {
          fetch("/delete_group", {
            method: "POST",
            body: JSON.stringify({ groupId: groupId }),
          }).then((_res) => {
            location.reload();
          });
    }
}