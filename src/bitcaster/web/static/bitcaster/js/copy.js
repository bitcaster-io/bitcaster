var $ = django.jQuery;

$(document).ready(function () {
    $(".clipboard").on('click', function () {
        var sender = $(this);
        var copyText = sender.text();
        navigator.clipboard.writeText(copyText);
        sender.addClass('copied');
        setTimeout(function () {
            sender.text(" Copied.")
        }, 400)
    });
})
