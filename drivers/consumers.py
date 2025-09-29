import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()


class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()
        # Add the connection to the "drivers" group
        await self.channel_layer.group_add("drivers", self.channel_name)

    async def disconnect(self, close_code):
        # Remove the connection from the "drivers" group
        await self.channel_layer.group_discard("drivers", self.channel_name)

    async def receive(self, text_data):
        # Ensure only authenticated drivers can send updates
        user = self.scope["user"]
        if not user.is_authenticated or user.type != "driver":
            await self.send(text_data=json.dumps({"error": "Unauthorized"}))
            return

        # Process incoming location data
        data = json.loads(text_data)
        driver_id = data["driver_id"]
        lat = data["lat"]
        lng = data["lng"]

        # Update driver's location in the database
        driver = User.objects.get(id=driver_id)
        driver.lat = lat
        driver.lng = lng
        driver.is_online = True
        driver.save()

        # Broadcast the update to all clients in the "drivers" group
        await self.channel_layer.group_send(
            "drivers",
            {
                "type": "driver_location_update",
                "driver_id": driver_id,
                "lat": lat,
                "lng": lng,
            },
        )

    async def driver_location_update(self, event):
        # Send the location update to the connected client
        await self.send(
            text_data=json.dumps(
                {
                    "driver_id": event["driver_id"],
                    "lat": event["lat"],
                    "lng": event["lng"],
                }
            )
        )
