import asyncio
import websockets
import threading

# 创建一个安全的队列，用于从输入线程接收消息
messages_queue = asyncio.Queue()

async def echo(websocket, path):
    secret_password = "secret123"
    await websocket.send(secret_password)
    response = await websocket.recv()
    if response == "correct":
        print("Password verified, connection established.")

        async def heartbeat():
            while True:
                try:
                    print("Sending heartbeat")
                    await websocket.ping()
                    await asyncio.sleep(10)  # 每10秒发送一次心跳
                except Exception as e:
                    print(f"Heartbeat failed: {e}")
                    break

        async def communicate():
            while True:
                message = await messages_queue.get()  # 从队列获取消息
                await websocket.send(message)
                client_response = await websocket.recv()
                print(f"Client response: {client_response}")

        await asyncio.gather(
            heartbeat(),
            communicate(),
        )
    else:
        print("Incorrect password, closing connection.")
        await websocket.close()

def start_input_thread():
    def read_input():
        while True:
            message = input("Enter message to send: ")
            asyncio.run_coroutine_threadsafe(messages_queue.put(message), asyncio.get_event_loop())
    threading.Thread(target=read_input, daemon=True).start()

start_server = websockets.serve(echo, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
start_input_thread()  # 启动输入线程
asyncio.get_event_loop().run_forever()
