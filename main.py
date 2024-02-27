import json

from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect


app = FastAPI()
clients: [int, WebSocket] = {}


async def start_game():
    packet = {
        "action": 1
    }

    for client in clients.values():
        await client.send_text(json.dumps(packet).encode())


async def broadcast(message: str, source: WebSocket):
    for client in clients.values():
        if client == source:
            continue

        await client.send_text(message)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()

    clients[client_id] = websocket

    if len(clients) == 2:
        await start_game()

    try:
        while True:
            message = await websocket.receive_text()
            await broadcast(message, websocket)

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
        del clients[client_id]
