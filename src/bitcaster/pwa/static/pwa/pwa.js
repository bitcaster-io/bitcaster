utils = {
    iOS: function () {
        return ['iPad Simulator',
                'iPhone Simulator',
                'iPod Simulator',
                'iPad',
                'iPhone',
                'iPod'
            ].includes(navigator.platform)
            // iPad on iOS 13 detection
            || (navigator.userAgent.includes("Mac") && "ontouchend" in document)
    },
    isMobile: function () {
        let check = false;
        (function (a) {
            if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) check = true;
        })(navigator.userAgent || navigator.vendor || window.opera);
        return check;
    },
    displayMode: function () {
        const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
        if (document.referrer.startsWith('android-app://')) {
            return 'twa';
        } else if (navigator.standalone || isStandalone) {
            return 'standalone';
        }
        return 'browser';
    },
    isApp: function () {
        return utils.displayMode() === 'standalone';
    },
    isBrowser: function () {
        return !utils.isApp();
    },
    urlBase64ToUint8Array: function (base64String) {
        let padding = '='.repeat((4 - base64String.length % 4) % 4)
        let base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/')

        let rawData = window.atob(base64)
        let outputArray = new Uint8Array(rawData.length)

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i)
        }
        return outputArray;
    },
    loadVersionBrowser: function () {
        if ("userAgentData" in navigator) {
            // navigator.userAgentData is not available in
            // Firefox and Safari
            const uaData = navigator.userAgentData;
            // Outputs of navigator.userAgentData.brands[n].brand are e.g.
            // Chrome: 'Google Chrome'
            // Edge: 'Microsoft Edge'
            // Opera: 'Opera'
            let browsername;
            let browserversion;
            let chromeVersion = null;
            for (var i = 0; i < uaData.brands.length; i++) {
                let brand = uaData.brands[i].brand;
                browserversion = uaData.brands[i].version;
                if (brand.match(/opera|chrome|edge|safari|firefox|msie|trident/i) !== null) {
                    // If we have a chrome match, save the match, but try to find another match
                    // E.g. Edge can also produce a false Chrome match.
                    if (brand.match(/chrome/i) !== null) {
                        chromeVersion = browserversion;
                    }
                    // If this is not a chrome match return immediately
                    else {
                        browsername = brand.substr(brand.indexOf(' ') + 1);
                        return {
                            name: browsername,
                            version: browserversion
                        }
                    }
                }
            }
            // No non-Chrome match was found. If we have a chrome match, return it.
            if (chromeVersion !== null) {
                return {
                    name: "chrome",
                    version: chromeVersion
                }
            }
        }
        // If no userAgentData is not present, or if no match via userAgentData was found,
        // try to extract the browser name and version from userAgent
        const userAgent = navigator.userAgent;
        let ua = userAgent, tem, M = ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
        if (/trident/i.test(M[1])) {
            let tem = /\brv[ :]+(\d+)/g.exec(ua) || [];
            return {name: 'IE', version: (tem[1] || '')};
        }
        if (M[1] === 'Chrome') {
            let tem = ua.match(/\bOPR\/(\d+)/);
            if (tem != null) {
                return {name: 'Opera', version: tem[1]};
            }
        }
        M = M[2] ? [M[1], M[2]] : [navigator.appName, navigator.appVersion, '-?'];
        if ((tem = ua.match(/version\/(\d+)/i)) != null) {
            M.splice(1, 1, tem[1]);
        }
        return {
            name: M[0],
            version: M[1]
        };
    },
    setBadge: function () {
        if (navigator.setAppBadge) {
            navigator.setAppBadge(arguments);
        } else if (navigator.setExperimentalAppBadge) {
            navigator.setExperimentalAppBadge(arguments);
        } else if (window.ExperimentalBadge) {
            window.ExperimentalBadge.set(arguments);
        }
    },
    clearBadge: function () {
        if (navigator.clearAppBadge) {
            navigator.clearAppBadge();
        } else if (navigator.clearExperimentalAppBadge) {
            navigator.clearExperimentalAppBadge();
        } else if (window.ExperimentalBadge) {
            window.ExperimentalBadge.clear();
        }
    },
    closeNotification: function () {
        navigator.serviceWorker.ready.then(reg => {
            reg.getNotifications().then(n => {
                for (let i = 0; i < n.length; i += 1) {
                    n[i].close();
                }
            });
        });
    }

}


var smartConsole = function (model, origConsole) {
    const self = this;
    self.model = model;

    if (!window.console || !origConsole) {
        origConsole = {};
    }

    var isDebug = false, isSaveLog = false,
        logArray = {
            logs: [],
            errors: [],
            warns: [],
            infos: []
        };
    self.log = function () {
        // var lineNum = 1 + logArray.length;
        let aa = Array.prototype.slice.call(arguments);
        let args = [];
        // var line = "";
        for (let i = 0; i < aa.length; i++) {
            if (typeof aa[i] !== 'string') {
                args.push(JSON.stringify(aa[i]))
            } else {
                args.push(aa[i])
            }
        }
        var line = args.join(" ");
        self.model.logger.push(line);
    }
    return {
        log: function () {
            self.log(Array.prototype.slice.call(arguments));
            this.addLog(arguments, "logs");
            isDebug && origConsole.log && origConsole.log.apply(origConsole, arguments);
        },
        warn: function () {
            this.addLog(arguments, "warns");
            isDebug && origConsole.warn && origConsole.warn.apply(origConsole, arguments);
        },
        error: function () {
            this.addLog(arguments, "errors");
            isDebug && origConsole.error && origConsole.error.apply(origConsole, arguments);
        },
        info: function (v) {
            this.addLog(arguments, "infos");
            isDebug && origConsole.info && origConsole.info.apply(origConsole, arguments);
        },
        debug: function (bool) {
            isDebug = bool;
        },
        saveLog: function (bool) {
            isSaveLog = bool;
        },
        addLog: function (arguments, array) {
            if (!isSaveLog) {
                return;
            }
            logArray[array || "logs"].push(arguments);
        },
        logArray: function () {
            return logArray;
        }
    };
}

var Steps = {
    LOADING: -1,
    LANDING: 0,
    INSTALL: 10,
    INSTALLLING: 20,
    REGISTER: 30,
    APP: 40,
    INSTALL_COMPLETE: 50,
    ALREADY_INSTALLED: 60,
    VERIFIED: 70,
};
let refreshing = false;


var MobileModel = function (params) {
    var self = this;

    // if (window.__init__) {
    //     window.__init__({msk: params.secret}).then(function () {
    //         Sentry.setTag("pwa", true);
    //         Sentry.setTag("pwa-key", params.secret);
    //     });
    // }
    self.params = params;
    const broadcast = new BroadcastChannel('bob-channel');
    window.console = smartConsole(self, window.console);
    // State
    self.version = ko.observable("-");
    self.state = ko.observable(null);
    self.verified = ko.observable(params.verified);
    self.loading = ko.observable(true);
    self.serviceWorker = ko.observable();
    self.serviceWorkerRegistration = ko.observable();
    self.bobRegistration = ko.observable(null);
    self.step = ko.observable(0);
    // UI
    self.bodyBackground = ko.observable(false);
    self.debug = ko.observable(false);
    // Registration
    self.deferredPrompt = ko.observable(null);
    self.installed = ko.observable(false);
    self.alreadyInstalled = ko.observable(null);
    self.installable = ko.computed(function () {
        return utils.isApp()
    })
    self.code = ko.observable(null);
    self.registered = ko.observable(null);
    // Messaging
    self.notificationStatus = ko.observable(null);
    self.notificationToken = ko.observable(false);

    self.position = ko.observable(null);
    self.positionStatus = ko.observable(null);
    self.notify = ko.observable({msg: "", level: ""});
    self.closeBanner = function () {
        self.notify({msg: "", level: ""});
    }
    self.numberOfAlarms = ko.observable(0);
    self.alarms = ko.observableArray([]);
    self.closeMessage = function () {
        self.numberOfAlarms(0);
        self.alarms([]);
    }
    // Operation
    self.invoked = ko.observable(false);
    self.isSender = ko.computed(function (e) {
        return self.state() && self.state().send_to !== "";
    })

    self.error = function (msg) {
        self.notify({msg: msg, level: "err"})
    }
    self.success = function (msg) {
        self.notify({msg: msg, level: "success"})
    }
    self.alarm = function (msg) {
        self.notify({msg: msg, level: "alarm"})
    }
    self.logger = ko.observableArray();
    self.group = ko.computed(function () {
        var state = self.state();
        if (state) {
            return state.send_to
        }
        return "";
    })
    self.isPageActive = function (page) {
        return this.step() === page;
    };

    self.step.subscribe(function (v) {
        console.log("STEP", v);
    })

    self.notificationStatus.subscribe(function (value) {
        console.log("notificationStatus", value);
    })
    self.numberOfAlarms.subscribe(function (value) {
        if (value > 0) {
            utils.setBadge(value);
        } else {
            utils.clearAppBadge();
        }
    })
    self.step.subscribe(function (value) {
        self.loading(false);
        switch (value) {
            case Steps.LOADING:
                self.loading(true);
                break;
            case Steps.LANDING:
                // code block
                break;
            case Steps.INSTALL:
                self.bodyBackground("install");
                break;
            case Steps.REGISTER:
                self.bodyBackground("install");
                break;
            case Steps.APP:
                self.bodyBackground("app");
                self.checkStatus();
                break;
            default:
            // code block
        }
    })

    window.addEventListener('beforeinstallprompt', function (e) {
        console.log("Event: beforeinstallprompt");
        if (self.verified()) {
            console.log("Code used");
        } else {
            e.preventDefault();
            localStorage.removeItem('reg');
            localStorage.removeItem('info');
            self.deferredPrompt(e);
            self.bobRegistration(null);
            self.state(null);
            self.loading(false);
            if (utils.isApp()) {
                self.step(Steps.REGISTER)
            } else {
                self.step(Steps.INSTALL);
            }
        }
    });

    self.syncManager = ko.observable();
    if (navigator.serviceWorker) {
        // navigator.serviceWorker.addEventListener('controllerchange', () => {
        //     if (!refreshing) {
        //         window.location.reload()
        //         refreshing = true
        //     }
        // });
        navigator.serviceWorker.ready.then((registration) => {
            console.log("serviceWorker is: ", (registration.active || registration.installing).state);
            self.serviceWorkerRegistration(registration);
            self.serviceWorker(registration.installing || registration.active);
        });
        if (navigator.getInstalledRelatedApps) {
            navigator.getInstalledRelatedApps().then(function (e) {
                console.log("getInstalledRelatedApps", e);
                self.alreadyInstalled(e.length > 0);
            })
        }
    }
    broadcast.onmessage = (event) => {
        console.log("broadcast.onmessage", event.data);
        if (event.data.action) {
            if (event.data.action === "setAppBadge") {
                self.numberOfAlarms(event.data.value);
            } else if (event.data.action === "check_status") {
                utils.checkStatus();
            } else if (event.data.action === "clearAppBadge") {
                utils.closeNotification();
                self.numberOfAlarms(0);
            } else if (event.data.action === "refresh_status") {
                self.checkStatus();
            }
        } else if (event.data.notification) {
            self.alarm(event.data.notification.message);
            self.alarms().push(event.data.notification.message)
            self.numberOfAlarms(self.numberOfAlarms() + 1)
            utils.checkStatus();
        } else if (event.data.message) {
            if (event.data.level === "ERROR") {
                self.error(event.data.message)
            } else if (event.data.level === "INFO") {
                self.success(event.data.message)
            }
        } else if (event.data.version) {
            self.version(event.data.version)
        }
    };
    self.state.subscribe(function (v) {
        self.saveState(v)
    });

    waitInstalled = function () {
        console.log("waitInstalled...")
        navigator.getInstalledRelatedApps().then(function (e) {
            console.log("getInstalledRelatedApps...", e);
            if (e.length === 0){
                setTimeout(waitInstalled, 2000);
            }else{
                self.step(Steps.INSTALL_COMPLETE);
                location.reload();
            }
        })
    };

    self.install = function () {
        console.log("install()")
        self.step(Steps.INSTALLLING);
        if (self.deferredPrompt()) {
            self.deferredPrompt().prompt();
            self.deferredPrompt().userChoice
                .then(function (choiceResult) {
                    console.log("deferredPrompt.userChoice.then", choiceResult.outcome)
                    if (choiceResult.outcome === 'accepted') {
                        if (navigator.getInstalledRelatedApps) {
                            waitInstalled();
                        } else {
                            setTimeout(() => {self.installed(true)}, 10000)
                        }
                    } else {
                        self.installing(false);
                    }
                    self.deferredPrompt(null);
                })
        } else {
            console.log("ERROR: No prompt available")
        }
    }

    self.update = function () {
        console.log("update()");
        let browser = utils.loadVersionBrowser(navigator.userAgent);
        let data = {
            "token": self.bobRegistration().token,
            "data": self.params.secret,
            "code": self.params.code,
            "ua_string": navigator.userAgent,
            'browser': browser.name.toUpperCase(),
            ...self.notificationToken(),
        };
        axios.post("/pwa/update/", data)
            .then(function (response) {
                console.log("Update success", response.data);
                localStorage.setItem("reg", window.btoa(JSON.stringify(response.data)));
                self.success("Update completed...")
                self.step(3);
                location.reload();
            })
            .catch(function (error) {
                console.log(error);
                Sentry.captureException(error);
                self.error("Errore");
            })
    }
    self.register = function () {
        console.log("register()");
        let browser = utils.loadVersionBrowser(navigator.userAgent);
        let data = {
            "data": self.params.secret,
            "code": self.code(),
            "ua_string": navigator.userAgent,
            'browser': browser.name.toUpperCase(),
            ...self.notificationToken(),
        };
        axios.post("/pwa/register/", data)
            .then(function (response) {
                console.log("Registration success", response.data);
                localStorage.setItem("reg", window.btoa(JSON.stringify(response.data)));
                self.success("Registration Completed...")
                self.step(3);
                location.reload();
            })
            .catch(function (error) {
                Sentry.captureException(error);
                self.error("Errore");
            })
    }
    self.saveState = function () {
        console.log("Saving state", self.state());
        localStorage.setItem("info", window.btoa(JSON.stringify(self.state())));
    }
    self.loadState = function () {
        console.log("loadState()");
        try {
            var state = JSON.parse(window.atob(localStorage.getItem("info")));
        } catch (e) {
            state = {}
        }
        self.state(state);
        console.log("Local State is ", state);
    }
    self.askForNotification = function () {
        console.log("askForNotification()")
        if (!self.serviceWorkerRegistration()) {
            console.log("Error: no serviceWorkerRegistration");
            return
        }

        self.serviceWorkerRegistration().pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: utils.urlBase64ToUint8Array(self.params.key)
        }).then(function (sub) {
            console.log("pushManager.subscribe");
            let endpointParts = sub.endpoint.split('/');
            let registration_id = endpointParts[endpointParts.length - 1];
            console.log("pushManager.subscribe registration_id", registration_id);
            let data = {
                'p256dh': btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey('p256dh')))),
                'auth': btoa(String.fromCharCode.apply(null, new Uint8Array(sub.getKey('auth')))),
                'registration_id': registration_id
            };
            self.notificationToken(data);
            self.notificationStatus(Notification.permission);
        }, function () {
            self.notificationStatus(Notification.permission);
        })
    }

    self.askForPosition = async function () {
        console.log("askForPosition()");
        if (!navigator.geolocation) {
            self.error("Geolocation is not supported by your browser");
        } else {
            navigator.geolocation.getCurrentPosition(function (pos) {
                self.position(pos);
                self.positionStatus("ok");
            }, function () {
                self.position(null);
                self.positionStatus("ok");
            }, {maximumAge: 1000 * 60 * 5, timeout: Infinity})
        }
    }

    self.checkNotification = function () {
        console.log(Notification.permission);
    }
    self.checkPosition = function () {
        navigator.geolocation.getCurrentPosition(function (pos) {
            console.log(pos)
            self.position(pos);
            self.positionStatus("ok");
        }, function () {
            console.log(pos)
            self.positionStatus("ok");
            self.position(null);
        })
    }
    updatePosition = setInterval(30000, function () {
        self.checkPosition();
    })

    self.checkStatus = function () {
        console.log("checkStatus()");
        self.loadRegistration();
        let registrationData = self.bobRegistration();
        axios.post("/pwa/status/", {
            "token": registrationData.token,
            "code": registrationData.code,
        }).then(function (response) {
            self.state(response.data);

            if (!response.data.selected) {
                self.error("App not enabled")
            }
        }).catch(function (err) {
            self.state({});
            // self.bobRegistration({});
            self.askForNotification();
            self.step(Steps.REGISTER);
            console.log(err);
            console.log(err.response.data);
        })
    }

    self.loadRegistration = function () {
        var registrationData;
        try {
            registrationData = JSON.parse(window.atob(localStorage.getItem("reg")));
        } catch (e) {
            registrationData = null;
        }
        self.bobRegistration(registrationData)
        console.log("registrationData: ", registrationData);
        return new Promise((resolve, reject) => {
            if (registrationData) {
                resolve(registrationData)
            } else {
                reject(registrationData);
            }
        });
    };
    var debugClick = 0
    self.debug.subscribe(function (value) {
        localStorage.setItem("debug", value);
        self.code(self.params.code);
    })
    self.timerId = ko.observable(null);
    self.buttonImage = ko.computed(function () {
        if (self.invoked()) {
            return self.params.static + "pwa/button/alarmed.png";
        } else if (self.timerId()) {
            return self.params.static + "pwa/button/pressed.gif";
        } else {
            return self.params.static + "pwa/button/default.png";
        }
    });
    self.canRegister = ko.computed(function () {
        return self.serviceWorker() && self.notificationToken();
    });
    self.canBeInstalled = ko.computed(function () {
        return (self.serviceWorker() && self.deferredPrompt());
    }, self);

    self.canSendHelp = ko.computed(function () {
        return (self.isSender() && self.bobRegistration());
    })
    self.countdown = ko.observable(false);
    self.clickDebug = function () {
        debugClick++;
        if (self.debug()) {
            self.debug(false)
            debugClick = 0
        } else if (debugClick >= 7) {
            debugClick = 0;
            self.debug(true);
        }
    };
    self.start = function () {
        console.log("screen.width", screen.width);
        console.log("screen.height", screen.height);
        console.log("userAgent", navigator.userAgent);
        if (!navigator.serviceWorker) {
            let msg = 'Sorry. This device does not support Bob technology. ';
            self.error(msg);
            Sentry.captureMessage(msg);
            return
        }
        if (self.verified() && utils.isBrowser()) {
            console.log("Code Used");
            self.step(Steps.VERIFIED);
            return;
        }
        if (utils.iOS()) {
            console.log("IOS detected");
        }
        self.debug(JSON.parse(localStorage.getItem("debug")));
        if (utils.isBrowser()) {  // browser
            console.log("Browser detected")
            self.serviceWorker.subscribe(function (e) {
                console.log("onServiceWorker.1", e)
                self.alreadyInstalled.subscribe(function (v) {
                    console.log("onAlreadyInstalled ", v);
                    if (v) {
                        self.step(Steps.ALREADY_INSTALLED)
                    } else {
                        self.step(Steps.INSTALL);
                        // if (utils.isMobile()) {
                        //     self.step(Steps.INSTALL);
                        // } else {
                        //     self.step(Steps.INSTALL);
                        // }
                    }
                })
            })
            navigator.serviceWorker.register('/pwa/serviceworker.js', {scope: '/pwa/'})
        } else if (utils.isApp()) {
            console.log("App detected")
            // navigator.serviceWorker.register('/pwa/serviceworker.js', {scope: '/pwa/'})
            self.serviceWorker.subscribe(function (e) {
                console.log("onServiceWorker.2", self.serviceWorker());
                if (e) {
                    self.positionStatus.subscribe(function (e) {
                        console.log("onPositionStatus", e)
                        self.askForNotification();
                    })
                    self.askForPosition();
                } else {
                    navigator.serviceWorker.register('/pwa/serviceworker.js', {scope: '/pwa/'})
                }
            });
            self.loadRegistration().then(function () {
                self.checkStatus();
                self.step(Steps.APP);
            }).catch(() => {
                self.serviceWorker.valueHasMutated();
                self.step(Steps.REGISTER);
            })
            // self.askForPosition();
            // self.askForNotification();
        } else {
            console.log("Unknown displayMode")
            self.error("Unknown displayMode")
        }
    }
    self.help = function () {
        if (self.timerId() === null) {
            return
        }
        self.touchEndHandler();
        let registrationData = self.bobRegistration();
        let pos = self.position()

        let data = {
            token: registrationData.token,
            code: registrationData.code,
            location: pos,
        };
        console.log("Help()", data);
        axios.post('/pwa/help/', data)
            .then(response => {
                self.invoked(true);
                self.success("Sent")
                console.log(response.data)
            })
            .catch((err) => {
                Sentry.captureException(err);
                if (err.response) {
                    console.log(err.response);
                    self.error(err.response.error);
                }
            });
    }


    self.touchStartHandler = function () {
        console.log("touchStartHandler");
        self.timerId(setInterval(self.help, 2000))
    }
    self.touchEndHandler = function () {
        clearInterval(self.timerId());
        self.timerId(null);
    }

}
window.addEventListener('load', function () {
    let pageModel;
    if (window.__init__) {
        let key = atob(document.getElementById("key").getAttribute("content"));
        window.__init__({msk: key}).then(function () {
            var params = JSON.parse(atob(document.getElementById("params").getAttribute("content")));
            Sentry.setTag("pwa", true);
            Sentry.setTag("pwa.key", params.secret);
            pageModel = new MobileModel(params);
            ko.applyBindings(pageModel)
            pageModel.start();
        });
    }
})
