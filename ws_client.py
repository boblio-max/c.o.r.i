import asyncio
import json
import logging
import threading
from queue import Queue, Empty
from typing import Optional, List

import websockets

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("ws_client")


class PersistentWebSocketClient:
    """
    Non-blocking persistent WebSocket client that runs in a background thread.
    
    Usage:
        client = PersistentWebSocketClient(host="192.168.1.20", port=8765)
        client.start()
        client.send([1, 2, 3, 4, 5, 6])  # Non-blocking
        client.stop()
    """

    def __init__(self, host: str, port: int, path: str = "/ws", timeout: float = 0.1):
        """
        Initialize the WebSocket client.
        
        Args:
            host: Server hostname/IP
            port: Server port
            path: WebSocket path (default "/ws")
            timeout: Send timeout in seconds
        """
        self.host = host
        self.port = port
        self.path = path
        self.timeout = timeout
        self.uri = f"ws://{host}:{port}{path}"
        
        self._send_queue = Queue()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._connected = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self):
        """Start the background connection thread."""
        if self._running:
            LOG.warning("Client already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()
        LOG.info("WebSocket client starting (connecting to %s)", self.uri)

    def stop(self):
        """Stop the background connection thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        LOG.info("WebSocket client stopped")

    def send(self, payload: List[float]) -> bool:
        """
        Non-blocking send of a payload to the server.
        
        Args:
            payload: List of numbers to send
            
        Returns:
            True if queued successfully, False if queue is full
        """
        if not self._running:
            LOG.warning("Client not running; ignoring send request")
            return False
        
        try:
            self._send_queue.put_nowait(payload)
            return True
        except Exception as e:
            LOG.error("Failed to queue payload: %s", e)
            return False

    def is_connected(self) -> bool:
        """Check if currently connected to server."""
        return self._connected

    def _run_event_loop(self):
        """Run the async event loop in a background thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._connection_loop())
        except Exception as e:
            LOG.exception("Event loop error: %s", e)
        finally:
            self._loop.close()

    async def _connection_loop(self):
        """Main connection loop with auto-reconnect."""
        backoff = 1
        max_backoff = 30
        
        while self._running:
            try:
                LOG.info("Connecting to %s", self.uri)
                async with websockets.connect(self.uri) as ws:
                    self._connected = True
                    LOG.info("Connected to server")
                    backoff = 1  # Reset backoff on successful connection
                    
                    try:
                        await self._message_loop(ws)
                    except Exception as e:
                        LOG.error("Message loop error: %s", e)
                        
            except Exception as e:
                self._connected = False
                LOG.warning("Connection failed: %s. Reconnecting in %d seconds...", e, backoff)
                await asyncio.sleep(backoff)
                backoff = min(max_backoff, backoff * 2)

    async def _message_loop(self, ws):
        """Handle sending messages from queue and receiving from server."""
        try:
            while self._running:
                # Check for outgoing messages
                try:
                    payload = self._send_queue.get_nowait()
                    message = json.dumps(payload, separators=(",", ":"))
                    await asyncio.wait_for(ws.send(message), timeout=self.timeout)
                    LOG.debug("Sent: %s", message)
                except Empty:
                    pass
                except asyncio.TimeoutError:
                    LOG.warning("Send timeout")
                except Exception as e:
                    LOG.error("Send error: %s", e)
                    raise
                
                # Small sleep to prevent busy-waiting and allow receiving
                await asyncio.sleep(0.01)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            LOG.error("Message loop exception: %s", e)
            raise
