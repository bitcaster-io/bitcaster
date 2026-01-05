from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model

User = get_user_model()


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        user = scope["user"]
        if user.is_anonymous:
            token = self.get_token(scope)
            if token:
                user = await self.get_user(token)
                if user:
                    scope["user"] = user

        return await super().__call__(scope, receive, send)

    def get_token(self, scope):
        headers = dict(scope.get("headers", []))
        auth = headers.get(b"authorization")

        if auth:
            try:
                prefix, token = auth.decode().split()
                if prefix.lower() == "bearer":
                    return token
            except ValueError:
                pass

        query_string = scope.get("query_string", b"").decode()
        return parse_qs(query_string).get("token", [None])[0]

    @database_sync_to_async
    def get_user(self, token):
        try:
            return User.objects.get(username=token)
        except User.DoesNotExist:
            return None
