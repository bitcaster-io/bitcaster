(function () {
    var origOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (method, url) {
        if (url.indexOf('/admin/autocomplete/') !== -1) {
            var pid = document.getElementById('id_project');
            if (pid && pid.value) {
                var sep = url.indexOf('?') === -1 ? '?' : '&';
                arguments[1] = url + sep + 'project_id=' + pid.value;
            }
        }
        return origOpen.apply(this, arguments);
    };
})();

(function wait() {
    if (typeof django !== 'undefined' && django.jQuery && typeof django.jQuery === 'function') {
        django.jQuery(function ($) {
            var $project = $('#id_project');
            var $app = $('#id_application');
            $project.on('change', function () {
                $app.find('option').remove();
                $app.append('<option value=""></option>');
                $app.val('').trigger('change');
            });
        });
    } else {
        setTimeout(wait, 10);
    }
})();
