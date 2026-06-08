# WebSocket server that forwards 6-number payloads to a registered Pi client.

import asyncio
import json
import logging
import argparse
from typing import Sequence, Optional, Any

import websockets
from websockets.exceptions import ConnectionClosedError

# Default network settings
HOST_DEFAULT = "0.0.0.0"
PORT_DEFAULT = 8765
WS_PATH = "/ws"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("ws_server")


# The WSServer class manages all the incoming connections.
class WSServer:
    """Async WebSocket server that keeps the last-connected client and sends JSON arrays."""

    def __init__(self):
        self._server: Optional[Any] = None
        self._last_client: Optional[Any] = None
        self._client_lock = asyncio.Lock()
        self._stopping = asyncio.Event()

    async def handler(self, websocket, path: Optional[str] = None) -> None:
        try:
            if path is None:
                path = getattr(websocket, "path", None)

            if path is not None and path != WS_PATH:
                LOG.warning("Rejected connection with unexpected path: %s", path)
                await websocket.close()
                return

            peer = websocket.remote_address
            LOG.info("Client connected: %s", peer)

            # This is the important part: a client can say "I'm the Pi" so the server 
            # knows who to forward the joint data to.
            async for msg in websocket:
                # Attempt to parse JSON
                try:
                    data = json.loads(msg)
                except Exception:
                    LOG.warning("Received non-JSON message from %s: %s", peer, msg)
                    continue

                # Registration message to mark this websocket as the Pi target
                if isinstance(data, dict) and data.get("role") == "pi":
                    async with self._client_lock:
                        self._last_client = websocket
                    LOG.info("Registered Pi client: %s", peer)
                    continue

                # If payload is a 6-number list, forward to registered Pi (if any)
                if isinstance(data, list) and len(data) == 6:
                    try:
                        numbers = [float(x) for x in data]
                    except Exception:
                        LOG.warning("Received non-numeric payload from %s: %s", peer, data)
                        continue

                    async with self._client_lock:
                        target = self._last_client

                    if target is None:
                        LOG.info("No Pi registered; dropping payload %s", numbers)
                        continue

                    # Don't forward back to sender if sender is the Pi
                    if websocket is target:
                        LOG.debug("Payload came from Pi itself; ignoring")
                        continue

                    sent = await self.publish(numbers)
                    LOG.info("Forwarded payload %s -> sent=%s", numbers, sent)
                    continue

                LOG.warning("Received unexpected message from %s: %s", peer, data)

        except Exception as e:
            LOG.exception("Unhandled error in handler: %s", e)
            try:
                await websocket.close(code=1011, reason=str(e))
            except Exception:
                pass
        finally:
            async with self._client_lock:
                if self._last_client is websocket:
                    self._last_client = None
            LOG.info("Client disconnected")
    async def start(self, host: str = HOST_DEFAULT, port: int = PORT_DEFAULT) -> None:
        LOG.info("Starting WebSocket server on %s:%d%s", host, port, WS_PATH)
        self._server = await websockets.serve(self.handler, host, port)
        LOG.info("WebSocket server started")

    async def stop(self) -> None:
        LOG.info("Stopping WebSocket server")
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        self._stopping.set()
        LOG.info("WebSocket server stopped")

    async def publish(self, payload: Sequence[float], timeout: float = 0.1) -> bool:
        """
        Send a JSON array of 6 numbers to the last-connected client (the Pi).

        Returns True on success, False if no client or send failed.
        Raises ValueError for invalid payload.
        """
        if not isinstance(payload, (list, tuple)) or len(payload) != 6:
            raise ValueError("payload must be a sequence of 6 numeric values")

        # Validate numeric types
        for i, v in enumerate(payload):
            if not isinstance(v, (int, float)):
                raise ValueError(f"payload element {i} is not numeric: {v!r}")

        message = json.dumps(list(payload), separators=(",", ":"))

        async with self._client_lock:
            client = self._last_client

        if client is None:
            LOG.info("No client connected; publish dropped")
            return False

        try:
            await asyncio.wait_for(client.send(message), timeout=timeout)
            LOG.debug("Published to client: %s", message)
            return True
        except asyncio.TimeoutError:
            LOG.warning("Publish timeout; clearing client")
        except ConnectionClosedError:
            LOG.info("Client connection closed during send; clearing client")
        except Exception as e:
            LOG.error("Unexpected error while sending: %s", e)

        # On any send failure, clear last client if it's closed
        async with self._client_lock:
            if self._last_client is client:
                self._last_client = None
        return False


# Convenience single-instance publisher that other modules can import:
publisher = WSServer()

# Import `publisher` and call `publish()` to send 6-number arrays to the Pi


def main() -> None:
    parser = argparse.ArgumentParser(description="WebSocket server for Raspberry Pi clients")
    parser.add_argument("--host", default=HOST_DEFAULT, help="Host to bind")
    parser.add_argument("--port", default=PORT_DEFAULT, type=int, help="Port to bind")
    parser.add_argument("--debug", action="store_true", help="Set logging to DEBUG")
    args = parser.parse_args()

    if args.debug:
        LOG.setLevel(logging.DEBUG)

    loop = asyncio.get_event_loop()
    server_task = loop.create_task(publisher.start(args.host, args.port))

    try:
        loop.run_until_complete(server_task)
        LOG.info("Server running. Press Ctrl+C to stop.")
        loop.run_forever()
    except KeyboardInterrupt:
        LOG.info("KeyboardInterrupt received; shutting down")
    finally:
        # Stop publisher and close loop
        loop.run_until_complete(publisher.stop())
        pending = asyncio.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        loop.close()


if __name__ == "__main__":
    main()