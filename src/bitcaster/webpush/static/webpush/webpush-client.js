!function (e) {
    var t = {};

    function r(n) {
        if (t[n]) return t[n].exports;
        var i = t[n] = {i: n, l: !1, exports: {}};
        return e[n].call(i.exports, i, i.exports, r), i.l = !0, i.exports
    }

    r.m = e, r.c = t, r.d = function (e, t, n) {
        r.o(e, t) || Object.defineProperty(e, t, {enumerable: !0, get: n})
    }, r.r = function (e) {
        "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(e, Symbol.toStringTag, {value: "Module"}), Object.defineProperty(e, "__esModule", {value: !0})
    }, r.t = function (e, t) {
        if (1 & t && (e = r(e)), 8 & t) return e;
        if (4 & t && "object" == typeof e && e && e.__esModule) return e;
        var n = Object.create(null);
        if (r.r(n), Object.defineProperty(n, "default", {
            enumerable: !0,
            value: e
        }), 2 & t && "string" != typeof e) for (var i in e) r.d(n, i, function (t) {
            return e[t]
        }.bind(null, i));
        return n
    }, r.n = function (e) {
        var t = e && e.__esModule ? function () {
            return e.default
        } : function () {
            return e
        };
        return r.d(t, "a", t), t
    }, r.o = function (e, t) {
        return Object.prototype.hasOwnProperty.call(e, t)
    }, r.p = "/", r(r.s = "PAM3")
}({
    PAM3: function (e, t) {
        function r(e) {
            return (r = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (e) {
                return typeof e
            } : function (e) {
                return e && "function" == typeof Symbol && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e
            })(e)
        }

        function n(e, t) {
            if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function")
        }

        function i(e, t) {
            for (var n = 0; n < t.length; n++) {
                var i = t[n];
                i.enumerable = i.enumerable || !1, i.configurable = !0, "value" in i && (i.writable = !0), Object.defineProperty(e, (o = i.key, u = void 0, u = function (e, t) {
                    if ("object" !== r(e) || null === e) return e;
                    var n = e[Symbol.toPrimitive];
                    if (void 0 !== n) {
                        var i = n.call(e, t || "default");
                        if ("object" !== r(i)) return i;
                        throw new TypeError("@@toPrimitive must return a primitive value.")
                    }
                    return ("string" === t ? String : Number)(e)
                }(o, "string"), "symbol" === r(u) ? u : String(u)), i)
            }
            var o, u
        }

        function o(e, t, r) {
            return t && i(e.prototype, t), r && i(e, r), Object.defineProperty(e, "prototype", {writable: !1}), e
        }

        function u(e) {
            for (var t = (e + "=".repeat((4 - e.length % 4) % 4)).replace(/\-/g, "+").replace(/_/g, "/"), r = window.atob(t), n = new Uint8Array(r.length), i = 0; i < r.length; ++i) n[i] = r.charCodeAt(i);
            return n
        }

        function s() {
            var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : "";
            throw new Error("Missing parameter " + e)
        }

        var a = function () {
            return Notification.requestPermission()
        }, c = function (e) {
            return navigator.serviceWorker.register(e).then((function (e) {
                return e
            }))
        }, p = function (e) {
            return e.pushManager.getSubscription()
        }, l = function () {
            function e() {
                var t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : s();
                n(this, e), this.url = t
            }

            return o(e, [{
                key: "register", value: function () {
                    var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : s(),
                        t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
                    return fetch(this.url, {
                        method: "POST",
                        mode: "cors",
                        credentials: "include",
                        cache: "default",
                        headers: new Headers({Accept: "application/json", "Content-Type": "application/json"}),
                        body: JSON.stringify({subscription: e, options: t})
                    }).then((function () {
                        return e
                    }))
                }
            }, {
                key: "updateOptions", value: function () {
                    var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : s(),
                        t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
                    return fetch(this.url, {
                        method: "PUT",
                        mode: "cors",
                        credentials: "include",
                        cache: "default",
                        headers: new Headers({Accept: "application/json", "Content-Type": "application/json"}),
                        body: JSON.stringify({subscription: e, options: t})
                    }).then((function () {
                        return e
                    }))
                }
            }, {
                key: "unregister", value: function () {
                    var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : s();
                    return fetch(this.url, {
                        method: "DELETE",
                        mode: "cors",
                        credentials: "include",
                        cache: "default",
                        headers: new Headers({Accept: "application/json", "Content-Type": "application/json"}),
                        body: JSON.stringify({subscription: e})
                    }).then((function () {
                        return !0
                    }))
                }
            }, {
                key: "ping", value: function () {
                    var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : s(),
                        t = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : {};
                    return fetch(this.url, {
                        method: "PING",
                        mode: "cors",
                        credentials: "include",
                        cache: "default",
                        headers: new Headers({Accept: "application/json", "Content-Type": "application/json"}),
                        body: JSON.stringify({subscription: e, options: t})
                    }).then((function () {
                        return !0
                    }))
                }
            }]), e
        }(), d = function () {
            function e(t) {
                var r = t.isSupported, i = void 0 === r ? s() : r, o = t.PermissionStatus,
                    u = t.ServiceWorkerRegistration, a = t.Subscription, c = t.applicationServerKey, p = t.subscribeUrl;
                n(this, e), this.supported = i, !1 !== i && (this.permissionStatus = o || s("permissionStatus"), this.registration = u || s("registration"), this.applicationServerKey = c || s("applicationServerKey"), this.subscription = a, void 0 !== p && (this.storage = new l(p)))
            }

            return o(e, [{
                key: "isSupported", value: function () {
                    return this.supported
                }
            }, {
                key: "ensureSupported", value: function () {
                    if (!this.isSupported()) throw Error("This browser does not support push notifications.")
                }
            }, {
                key: "ensureUrlIsProvided", value: function () {
                    if (!this.storage) throw Error("Webpush client error: subscribeUrl has not been provided.");
                    return !0
                }
            }, {
                key: "isUrlProvided", value: function () {
                    return !!this.storage
                }
            }, {
                key: "getPermissionState", value: function () {
                    return this.ensureSupported(), this.permissionStatus
                }
            }, {
                key: "getSubscription", value: function () {
                    return this.subscription
                }
            }, {
                key: "subscribe", value: function () {
                    var e = this, t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {},
                        r = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : this.isUrlProvided();
                    return this.ensureSupported(), this.registration.pushManager.subscribe({
                        userVisibleOnly: !0,
                        applicationServerKey: this.applicationServerKey
                    }).then((function (n) {
                        return e.subscription = n, !0 === r && e.ensureUrlIsProvided() ? e.storage.register(n, t) : new Promise((function (e) {
                            return e(n)
                        }))
                    }))
                }
            }, {
                key: "unsubscribe", value: function () {
                    var e = this,
                        t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : this.isUrlProvided();
                    return this.ensureSupported(), p(this.registration).then((function (r) {
                        r.unsubscribe().then((function () {
                            return e.subscription = null, !0 === t && e.ensureUrlIsProvided() ? e.storage.unregister(r) : new Promise((function (e) {
                                return e(!0)
                            }))
                        }))
                    }))
                }
            }, {
                key: "updateOptions", value: function () {
                    var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {};
                    return this.ensureSupported(), this.ensureUrlIsProvided(), this.storage.updateOptions(this.subscription, e)
                }
            }, {
                key: "ping", value: function () {
                    var e = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : {};
                    return this.ensureSupported(), this.ensureUrlIsProvided(), this.storage.ping(this.subscription, e)
                }
            }]), e
        }();
        window.WebPushClientFactory = {
            isSupported: function () {
                return "PushManager" in window && "fetch" in window && "permissions" in navigator && "serviceWorker" in navigator
            }, create: function (e) {
                var t = e.serviceWorkerPath, r = e.subscribeUrl, n = e.serverKey;
                return this.isSupported() ? a().then((function (e) {
                    return c(t).then((function (t) {
                        return p(t).then((function (i) {
                            return new d({
                                isSupported: !0,
                                applicationServerKey: u(n),
                                PermissionStatus: e,
                                ServiceWorkerRegistration: t,
                                Subscription: i,
                                subscribeUrl: r
                            })
                        }))
                    })).catch((function (e) {
                        return console.warn("Webpush client cannot be started: " + e), new d({isSupported: !1})
                    }))
                })) : new Promise((function (e) {
                    e(new d({isSupported: !1}))
                }))
            }
        }
    }
});
