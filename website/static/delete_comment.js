
$(document).ready(function() {
    // 监听所有的删除按钮
    $(document).on('click', '.delete-button', function() {
        // 获取评论的ID
        const commentId = $(this).closest('.comment').data('comment-id');

        // 确认删除
        if(!confirm('Are you sure you want to delete this comment?')) {
            return;
        }

        // 发送AJAX请求到服务器删除评论
        $.ajax({
            type: 'POST',
            url: '/delete_comment/' + commentId,
            success: function(response) {
                if (response.success) {
                    // 如果成功，则从页面上移除这个评论
                    $(`div[data-comment-id="${commentId}"]`).parent().remove();
                } else {
                    alert('Error deleting comment.');
                }
            },
            error: function() {
                alert('Error communicating with the server.');
            }
        });
    });
});



