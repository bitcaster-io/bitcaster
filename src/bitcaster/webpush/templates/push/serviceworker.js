/* WebPush sw {{ version }}
*
// */
var _ = "{% load static %}";
self.addEventListener('install', function (event) {
    console.log("SW: install");
    self.skipWaiting();
});
console.log(22222, "SW:")



self.addEventListener('push', function (event) {
    console.log("SW: push", event.data.text());
    var message, tag, data;
    var title = "Bitcaster"
    // var icon = ""
    // var badge = ""
    try {
        var payload = event.data.json();
        if (payload) {
            title = payload.subject || title;
            message = payload.message;
            tag = payload.tag || "";
            icon = payload.icon || icon;
            data = payload.data || null;
            image = payload.image || null;
        }
    } catch (err) {
        console.log(err);
        message = event.data.text();
    }
    var logo = "{% static 'bitcaster/images/logos/ico/android-chrome-512x512.png' %}"

    // right image
    var icon = "{% static 'bitcaster/images/logos/ico/android-chrome-192x192.png' %}"
    var badge = "{% static 'bitcaster/images/logos/ico/favicon-24x24.png' %}"
    var image = "{% static 'bitcaster/images/logos/logo800.png' %}"
    var options = {
        // data: data,
        body: message,
        icon: icon,
        image: image,
        // tag: tag,
        // image: "",
        badge: badge,
        // vibrate: [200, 100, 200, 100, 200, 100, 200]
    }
    console.log("SW: registration", self.registration);

    try {
        self.registration.showNotification(title, options);
        console.log("SW: showNotification", title, options);
    } catch (err) {
        console.log(err);
    }
});
