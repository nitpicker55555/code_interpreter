import asyncio
import websockets

async def listen():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # 接收服务器发送的密码
        password = await websocket.recv()
        print(f"Received password from server: {password}")

        correct_password = "secret123"

        # 验证密码
        if password == correct_password:
            print("Password verified.")
            await websocket.send("correct")

            # 密码正确，进入接收消息循环
            while True:
                message = await websocket.recv()
                print(f"Received message from server: {message}")
                # 回复服务器，确认消息已收到
                await websocket.send("收到")
        else:
            print("Password incorrect.")
            await websocket.send("incorrect")

asyncio.get_event_loop().run_until_complete(listen())
