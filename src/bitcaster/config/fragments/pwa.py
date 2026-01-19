from ..settings import env

PWA_APP_SUFFIX = ""

PWA_APP_NAME = "Bitcaster"
PWA_APP_DESCRIPTION = "Bitcaster mobile app"
PWA_APP_THEME_COLOR = "#00a8b5"
PWA_APP_BACKGROUND_COLOR = "#00a8b5"
PWA_APP_DISPLAY = "standalone"
PWA_APP_DEBUG_MODE = True
PWA_APP_SCOPE = "/pwa/"
PWA_APP_ORIENTATION = "any"
PWA_APP_START_URL = "/pwa/"
PWA_APP_STATUS_BAR_COLOR = "default"
PWA_APP_ICONS = [
    {"src": "/static/bob/images/favicons/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "/static/bob/images/favicons/android-chrome-256x256.png", "sizes": "256x256", "type": "image/png"},
]
PWA_APP_ICONS_APPLE = [
    {"src": "/static/bob/images/favicons/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}
    # {
    #     'src': '/static/images/my_apple_icon.png',
    #     'sizes': '160x160'
    # }
]
PWA_APP_SPLASH_SCREEN = [
    {
        "src": "/static/bob/images/bob_error.svg",
        "media": "(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)",
    }
]
PWA_APP_DIR = "ltr"
PWA_APP_LANG = "en-US"
