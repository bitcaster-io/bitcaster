var $ = django.jQuery;

var g;
$(".clipboard").on('click', function () {
    var sender = $(this);
    var copyText = sender.text();
    navigator.clipboard.writeText(copyText);
    sender.addClass('copied');
    sender.text(" Copied to clipboard...")
    setTimeout(function () {
        sender.removeClass("copied");
        sender.text(copyText)
    }, 400)
});
