from bitcaster.config import env

ROOT_TOKEN = env("ROOT_TOKEN")
ROOT_TOKEN_HEADER = env("ROOT_TOKEN_HEADER", default="x-root-token")
