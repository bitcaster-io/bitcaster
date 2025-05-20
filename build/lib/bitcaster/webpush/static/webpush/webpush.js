$(function () {
    // var secret = $("meta[name=s]").attr("content");
    // var serviceWorkerPath = `/webpush/subscribe/${secret}`;
    // var serverKey = $("meta[name=key]").attr("content");
    // var subscribeUrl = $("meta[name=url]").attr("content");
    var WebPushClient;
    fetch(location.href + "data/", {method: "GET"})
        .then(response => response.json())
        .then(data => {
            var serviceWorkerPath = data.w;
            var serverKey = data.k;
            var subscribeUrl = data.s;
            var unSubscribeUrl = data.u;
            if (WebPushClientFactory.isSupported()) {
                WebPushClientFactory.create({
                    serviceWorkerPath: serviceWorkerPath, // Public path to the service worker
                    serverKey: serverKey, // https://developers.google.com/web/fundamentals/push-notifications/web-push-protocol#application_server_keys
                    subscribeUrl: subscribeUrl, // Optionnal - your application URL to store webpush subscriptions
                })
                    .then(Client => {
                        WebPushClient = Client;
                        if (WebPushClient.permissionStatus === "denied") {
                            $("#permissionDenied").show();
                        }
                        if (WebPushClient.permissionStatus === "granted") {
                            $("#supported").show();
                        }
                    });

            } else {
                $("#unsupported").show();
                $("#supported").hide();
            }
            $("#subscribe").on("click", function () {
                WebPushClient.subscribe().then(c => location.reload())
            })
            $("#deny").on("click", function () {
                fetch(unSubscribeUrl, {method: "POST"}).then((function () {
                    location.reload();
                }))
            })


        })

})
