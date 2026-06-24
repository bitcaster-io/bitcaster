var $ = django.jQuery;

function Editor() {
    var self = this;
    self.setup = function (ed) {
        self.$context = $("#id_context");
        self.$subject = $("#id_subject");
        self.$content = $("#id_content");
        self.csrftoken = $("[name=csrfmiddlewaretoken]").val();
        self.render_url = $("meta[name='render-url']").attr("content");
        self.test_url = $("meta[name='test-url']").attr("content");
        self.change_url = $("meta[name='change-url']").attr("content");
        self.iframeElement = document.getElementById("preview");
        self.mdEditor = null;
        self.ACTIVE = null;

        (function waitForAceEditor() {
            if (typeof ace === "undefined") {
                return setTimeout(waitForAceEditor, 50);
            }

            const aceDiv = document.querySelector(".ace_editor");

            if (!aceDiv) {
                return setTimeout(waitForAceEditor, 50);
            }

            self.mdEditor = ace.edit(aceDiv); // 🔥 istanza reale, già creata

            self.mdEditor.session.on("change", function () {
                send();
            });
        })();

        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", self.csrftoken);
                }
            }
        });


        self.$context.on("change", function () {
            send()
        })
        self.$content.on("keyup", function () {
            send()
        })
        self.$subject.on("keyup", function () {
            send()
        })
        $("#btn_test").on("click", function (e) {
            send_message();
        })

        $(".button.toggler").on("click", function (e) {
            $(".button.toggler").removeClass("active");
            $(".tab").hide();
            self.ACTIVE = $(this);
            $($(self.ACTIVE).data("panel")).show();
            self.ACTIVE.addClass("active");
            send();
        })
        $("#btn_content").click();
        setupTinyMCE(ed)
        $(".button.toggler:first").click()
    }

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function replaceIframeContent(newHTML) {
        self.iframeElement.src = "about:blank";
        self.iframeElement.contentWindow.document.open();
        self.iframeElement.contentWindow.document.write(newHTML);
        self.iframeElement.contentWindow.document.close();
    }

    var pendingTestXHR = null;
    function send_message() {
        if (pendingTestXHR) {
            pendingTestXHR.abort();
        }
        pendingTestXHR = django.jQuery.post(self.test_url, {
                "content_type": "text/plain",
                "recipient": $("#id_recipient").val(),
                "subject": self.$subject.val(),
                "content": self.$content.val(),
                "html_content": tinymce.activeEditor.getContent("id_html_content"),
                "context": self.$context.val()
            },
        );
    }

    var pendingXHR = null;
    function send() {
        var selected = self.ACTIVE.attr("id");
        var content = "";
        var context = self.$context.val();
        if (selected === "btn_md") {
            if (self.mdEditor) content = self.mdEditor.getValue();
        } else if (selected === "btn_html") {
            content = tinymce.activeEditor.getContent("id_html_content");
        } else if (selected === "btn_subject") {
            content = self.$subject.val()
        } else if (selected === "btn_content") {
            content = self.$content.val()
        } else {
            return
        }
        var payload = {
            "content_type": $(self.ACTIVE).data("content-type"),
            "content": content,
            "context": context,
            "recipient": $("#id_recipient").val(),
        }
        if (pendingXHR) {
            pendingXHR.abort();
        }
        pendingXHR = django.jQuery.post(self.render_url, payload,
            function (data) {
                replaceIframeContent(data);
                pendingXHR = null;
            }
        );
    }

    function gotoParent() {
        var base = window.location.href;
        var parent = base.split("/").slice(0, -2).join("/")
        return parent + "/change/";
    }

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
}

editor = new Editor()

function setupTinyMCE(ed) {
    $(document).ready(function () {
        editor.setup(ed)
    })
}
