function deleteGroupAndPosts(groupId) {
    if (confirm("Confirm to delete this group?")) {
          fetch("/delete_group", {
            method: "POST",
            body: JSON.stringify({ groupId: groupId }),
          }).then((_res) => {
            location.reload();
          });
    }
}