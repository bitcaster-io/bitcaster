import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class ChromePluginConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
            self.group_name = f"user_{self.scope['user'].pk}_chromeplugin"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            logger.info(f"User {self.scope['user']} connected to WebSocket and joined group {self.group_name}")
        else:
            await self.close()
            logger.warning("Unauthenticated user tried to connect to WebSocket.")

    async def disconnect(self, code):
        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"User {self.scope['user']} disconnected from WebSocket.")

    async def chromeplugin_message(self, event):
        message = event["message"]
        await self.send_json(content=message)
        logger.debug(f"Sent message to {self.scope['user']} via WebSocket.")
