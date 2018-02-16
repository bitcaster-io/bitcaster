/**
 *
 * User: sax
 * Date: 28/09/14
 * Time: 12:22
 *
 */

query_filter = function(term){
    return {
        name__istartswith: term
    };
};

function apply_lookup(TARGET, lookup_url, options) {
    if (options === undefined) options = {};
    if (options.placeholder === undefined) options.placeholder = "Select";
    if (options.minimumInputLength === undefined) options.minimumInputLength = 2;
    if (options.ajax === undefined) options.ajax = {};
    if (options.ajax.data === undefined) options.ajax.data = query_filter;

    $(TARGET).select2({
        placeholder: options.placeholder,
        multiple: false,
        allowClear: true,
        minimumInputLength: options.minimumInputLength,
        initSelection: function (element, callback) {
            var id = $(element).val();
            if (id !== "") {
                $.ajax(lookup_url + "?id=" + id, {
                    dataType: "json"
                }).done(function (data) {
                    $(TARGET).select2("data", data[0]);
                });
            }
        },
        ajax: {
            url: lookup_url,
            dataType: 'json',
            type: "GET",
            cache: false,
            quietMillis: 500,
            data: options.ajax.data,
            results: function (data) {
                return {results: data};
            }

        }
    });
}
