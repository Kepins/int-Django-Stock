import json

from channels.generic.websocket import AsyncWebsocketConsumer


class HomeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user_id = self.scope["cookies"].get("ws_token")

        self.group_name = f"user_{user_id}"  # Set the group name

        # Add the client to the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_stock_update(self, event):
        # Send a custom message to the client
        await self.send(text_data=json.dumps(event))
