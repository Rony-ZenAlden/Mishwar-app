from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()


class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"user_{self.user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def trip_status(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "trip_status",
                    "status": event["status"],
                    "message": event.get("message"),
                    "trip_id": event.get("trip_id"),
                    "driver_phone": event.get("driver_phone"),
                    "driver_lat": event.get("driver_lat"),
                    "driver_lng": event.get("driver_lng"),
                    "distance": event.get("distance"),
                    "duration": event.get("duration"),
                }
            )
        )

    async def payment_confirmed(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "payment_confirmed",
                    "trip_id": event["trip_id"],
                    "message": event["message"],
                }
            )
        )


class DriverConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.driver_id = self.scope["url_route"]["kwargs"]["driver_id"]
        self.group_name = f"driver_{self.driver_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def trip_request(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "new_trip",
                    "trip_id": event["trip_id"],
                    "start_lat": str(event["start_lat"]),
                    "start_lng": str(event["start_lng"]),
                    "destination": event["destination"],
                }
            )
        )

    async def trip_accepted(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "trip_accepted",
                    "trip_id": event["trip_id"],
                    "user_phone": event["user_phone"],
                    "user_lat": event["user_lat"],
                    "user_lng": event["user_lng"],
                    "destination_address": event["destination_address"],
                    "destination_lat": event["destination_lat"],
                    "destination_lng": event["destination_lng"],
                }
            )
        )

    async def location_update(self, event):
        await self.send(
            text_data=json.dumps(
                {"type": "location_update", "lat": event["lat"], "lng": event["lng"]}
            )
        )

    async def cash_payment_selected(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "cash_payment_selected",
                    "trip_id": event["trip_id"],
                    "price": event["price"],
                }
            )
        )

    async def payment_confirmed(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "payment_confirmed",
                    "trip_id": event["trip_id"],
                    "message": event["message"],
                }
            )
        )


class TripConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.trip_id = self.scope["url_route"]["kwargs"]["trip_id"]
        self.group_name = f"trip_{self.trip_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        print(f"Received message: {text_data}")
        try:
            data = json.loads(text_data)
            message_type = data.get("type")
            if message_type == "location_update":
                required_keys = ["lat", "lng", "user_id"]
                if all(key in data for key in required_keys):
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            "type": "location_update",
                            "lat": data["lat"],
                            "lng": data["lng"],
                            "user_id": data["user_id"],
                        },
                    )
            elif message_type == "driver_arrived":
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "driver_arrived",
                        "user_id": data["user_id"],
                    },
                )
            elif message_type == "user_boarded":
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "user_boarded",
                        "user_id": data["user_id"],
                    },
                )
            else:
                print(f"Received unknown message type: {message_type}")
        except json.JSONDecodeError as e:
            print(f"Received invalid JSON: {text_data}, Error: {e}")

    async def location_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "location_update",
                    "lat": event["lat"],
                    "lng": event["lng"],
                    "user_id": event["user_id"],
                }
            )
        )

    async def driver_arrived(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "driver_arrived",
                    "user_id": event["user_id"],
                }
            )
        )

    async def user_boarded(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_boarded",
                    "user_id": event["user_id"],
                }
            )
        )

    async def trip_started(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "trip_started",
                    "trip_id": event["trip_id"],
                    "start_lat": event["start_lat"],
                    "start_lng": event["start_lng"],
                    "destination_lat": event["destination_lat"],
                    "destination_lng": event["destination_lng"],
                }
            )
        )

    async def trip_ended(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "trip_ended",
                    "trip_id": event["trip_id"],
                    "start_lat": event["start_lat"],
                    "start_lng": event["start_lng"],
                    "destination_lat": event["destination_lat"],
                    "destination_lng": event["destination_lng"],
                    "price": event["price"],  # to include the price
                }
            )
        )
