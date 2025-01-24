import asyncio
import websockets
import random
import json
import settings

clients = set()

available_emails = []


async def broadcast_message(message):
    """
    Sends a message to all connected clients.
    """
    if clients:
        await asyncio.gather(*(client.send(message) for client in clients))


async def handler(websocket):
    """
    Handles incoming WebSocket connections and messages.
    """
    clients.add(websocket)
    try:
        async for message in websocket:
            try:
                message_dict = json.loads(message)

                if message_dict["action"] == "send-tmp-mail":
                    available_emails.append(message_dict["value"])

                if message_dict["action"] == "send-verification-code":
                    print(
                        {"action": "verification-code", "value": message_dict["value"]}
                    )
                    await broadcast_message(
                        json.dumps(
                            {
                                "action": "verification-code",
                                "value": message_dict["value"],
                            }
                        )
                    )

                if message_dict["action"] == "get-tmp-mail":
                    email_choose = random.choice(available_emails)
                    available_emails.remove(email_choose)
                    await broadcast_message(
                        json.dumps({"action": "email-found", "value": email_choose})
                    )

                if message_dict["action"] == "get-verification-code":
                    await broadcast_message(
                        json.dumps({"action": "get-verification-code"})
                    )
            except Exception as e:
                print("Error: Verify the content type!!!", e)

    except websockets.exceptions.ConnectionClosed:
        print("Connection closed.")
    finally:
        clients.remove(websocket)


async def main():
    server = await websockets.serve(handler, "localhost", settings.websocket_port)
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
