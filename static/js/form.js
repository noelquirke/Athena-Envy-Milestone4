//function to match email field to username field before submitting
$().ready(function() {
    $("#create-account").click(function() {
        $('#id_username').val($('#id_email').val());
    });
})
