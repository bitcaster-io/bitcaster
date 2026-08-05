var $ = django.jQuery;

$(document).ready(function () {
    var $containers = $('.clipboard');

    $containers.on('click', function () {
        var $sender = $(this);
        var originalText = $sender.text();

        // 1. Copy text to clipboard
        navigator.clipboard.writeText(originalText);

        // 2. Check for .subst class
        if ($sender.hasClass('subst')) {
            // BEHAVIOR 1: Replace text directly inside the container

            // Prevent multiple rapid clicks from corrupting the stored text
            if ($sender.data('is-copying')) return;
            $sender.data('is-copying', true);

            $sender.text('Copied!');

            setTimeout(function () {
                $sender.text(originalText);
                $sender.data('is-copying', false);
            }, 1200);

        } else {
            // BEHAVIOR 2: Display floating badge in top-right corner

            $sender.find('.copied-badge').remove(); // Clear any existing badge

            $('<div class="copied-badge">Copied</div>')
                .hide()
                .appendTo($sender)
                .fadeIn(200)
                .delay(1200)
                .fadeOut(400, function () {
                    $(this).remove(); // Cleanup from DOM
                });
        }
    });
});
