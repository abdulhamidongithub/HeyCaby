from rest_framework_simplejwt.tokens import AccessToken
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs


class WebSocketTokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        token = query_params.get("token")

        if token:
            access_token = token[0]
            user = await self.get_user_from_token(access_token)
            if user:
                scope["user"] = user

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, access_token):
        try:
            valid_token = AccessToken(access_token)
            user = valid_token.payload.get("user_id")
            return user
        except:
            return None
