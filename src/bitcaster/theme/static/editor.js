var $ = django.jQuery;
var $context = $("#id_context");
var $subject = $("#id_subject");
var $content = $("#id_content");
var csrftoken = $("[name=csrfmiddlewaretoken]").val();
var url = $("#editor-script").data("url");
var iframeElement = document.getElementById("preview")

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function replaceIframeContent(newHTML) {
    iframeElement.src = "about:blank";
    iframeElement.contentWindow.document.open();
    iframeElement.contentWindow.document.write(newHTML);
    iframeElement.contentWindow.document.close();
}

function send() {
    var context = $context.val();
    var content = $content.val();
    var subject = $subject.val();
    var html_content = tinymce.activeEditor.getContent("id_html_content");
    django.jQuery.post(url, {
            "subject": subject,
            "html_content": html_content,
            "content": content,
            "context": context
        },
        function (data) {
            replaceIframeContent(data)
        }
    );
}

$context.on("change", function () {
    send()
})
$(".btn").on("click", function(e){
    $(".tab").hide();
    $($(this).data("panel")).show()
})
function setupTinyMCE(ed) {
    var typingTimer;                //timer identifier
    var doneTypingInterval = 500;  //time in ms, 5 seconds for example
    ed.on("keydown", function () {
        clearTimeout(typingTimer);
    })
    ed.on("change", function () {
        send();
    })
    ed.on("keyup", function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(send, doneTypingInterval);
    })
}
