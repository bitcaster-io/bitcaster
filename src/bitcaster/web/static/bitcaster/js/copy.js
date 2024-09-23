var $ = django.jQuery;

$(document).ready(function () {
    $(".clipboard").on('click', function () {
        var sender = $(this);
        var copyText = sender.text();
        navigator.clipboard.writeText(copyText);
        sender.addClass('copied');
        sender.text(" Copied.")
        setTimeout(function () {
            sender.removeClass("copied");
            sender.text(copyText)
        }, 400)
    });
})
