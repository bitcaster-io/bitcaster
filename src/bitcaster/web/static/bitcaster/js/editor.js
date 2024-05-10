var $ = django.jQuery;
var $context = $("#id_context");
var $subject = $("#id_subject");
var $content = $("#id_content");
var csrftoken = $("[name=csrfmiddlewaretoken]").val();
var render_url = $("meta[name='render-url']").attr("content");  ;
var test_url = $("meta[name='test-url']").attr("content");  ;
var change_url = $("meta[name='change-url']").attr("content");  ;
var iframeElement = document.getElementById("preview");
var ACTIVE=null;

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

function send_message() {
    django.jQuery.post(test_url, {
            "content_type": "text/plain",
            "recipient": $("#id_recipient").val(),
            "subject": $subject.val(),
            "content":  $content.val(),
            "html": tinymce.activeEditor.getContent("id_html_content"),
            "context": $context.val()
        },
    );
}
function send() {
    var selected = ACTIVE.attr("id");
    var content = "";
    var context = $context.val();
    if (selected === "btn_html"){
        content = tinymce.activeEditor.getContent("id_html_content");
    }else if (selected === "btn_subject"){
        content = $subject.val()
    }else if (selected === "btn_content"){
        content = $content.val()
    }else{
        return
    }

    django.jQuery.post(render_url, {
            "content_type": $(ACTIVE).data("content-type"),
            "content": content,
            "context": context
        },
        function (data) {
            replaceIframeContent(data)
        }
    );
}
function gotoParent(){
    var base = window.location.href;
    var parent = base.split("/").slice(0,-2).join("/")
    return parent + "/change/";
}

$context.on("change", function () {
    send()
})
$content.on("keyup", function () {
    send()
})
$("#btn_test").on("click", function(e){
    send_message();
})

$(".button.toggler").on("click", function(e){
    $(".tab").hide();
    ACTIVE = $(this);
    $($(ACTIVE).data("panel")).show();
    send();
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

$("#btn_content").click();
