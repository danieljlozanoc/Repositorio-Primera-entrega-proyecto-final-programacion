# client_transport.py
# pip install websockets
# Do not modify this file. 
# Perform your client-side testing by modifying test_client.py after running the websocket_erver.

import asyncio
import websockets
import json
import threading

class GameClient:

    def __init__(self, uri="ws://localhost:8765", response_handler=None):
        self.uri = uri
        self.response_handler = response_handler
        self.websocket = None
        # Create the loop but don't set it as the main thread's loop
        self.loop = asyncio.new_event_loop()
        self.thread = None

    # ------------------------
    # INTERNAL ASYNC METHODS
    # ------------------------

    async def _connect(self):
        self.websocket = await websockets.connect(self.uri)
        # Schedule the listener task within the loop
        self.loop.create_task(self._listen())

    async def _send(self, data):
        if self.websocket:
            await self.websocket.send(json.dumps(data))

    async def _receive(self):
        # This will now stay active in the background thread
        response = await self.websocket.recv()
        return json.loads(response)

    async def _close(self):
        if self.websocket:
            await self.websocket.close()
        self.loop.stop()

    async def _listen(self):
        try:
            while True:
                response = await self._receive()
                if self.response_handler:
                    # If your handler does UI work, ensure it's thread-safe!
                    self.response_handler(response)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server.")

    # ------------------------
    # PUBLIC SYNC INTERFACE
    # ------------------------

    def connect(self):
        """Starts the loop in a background thread and connects."""
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()
        # Use run_coroutine_threadsafe to talk to the background loop
        future = asyncio.run_coroutine_threadsafe(self._connect(), self.loop)
        return future.result() # Wait for connection to establish

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def send_action(self, action, **kwargs):
        """Thread-safe way to send messages from the main thread."""
        message = {"action": action}
        message.update(kwargs)
        asyncio.run_coroutine_threadsafe(self._send(message), self.loop)

    def close(self):
        """Gracefully shut down the connection and the thread."""
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._close(), self.loop)
        if self.thread:
            self.thread.join(timeout=1)