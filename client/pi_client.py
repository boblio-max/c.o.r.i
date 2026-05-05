import asyncio
import json
import logging
import argparse
from typing import List

# Third-party imports
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

# Set up logging
LOG = logging.getLogger("pi_client")
WS_PATH = "/ws"

try:
    from adafruit_servokit import ServoKit
except ImportError:
    ServoKit = None
    LOG.warning("adafruit_servokit not found. Actuation will be disabled.")

async def handle_payload(values: List[float], actuate: bool, kit: 'ServoKit | None'):
    """Handles the actual movement of servos based on received values."""
    if len(values) != 6:
        LOG.warning("Received payload with wrong length: %s", values)
        return

    if actuate:
        if kit is None:
            LOG.error("Actuation requested but ServoKit is not initialized")
            return
        
        # Map values to servo angles
        for i, v in enumerate(values):
            # Ensure the value is within standard servo bounds (0-180)
            angle = max(0, min(180, int(v)))
            try:
                kit.servo[i].angle = angle
            except Exception as e:
                LOG.error("Failed to set servo %d to angle %d: %s", i, angle, e)
        LOG.info("Actuated servos with %s", values)
    else:
        LOG.info("Payload (dry-run): %s", values)


async def listen_loop(uri: str, actuate_flag: bool, dry_run: bool, max_backoff: int):
    """Main WebSocket connection and message handling loop."""
    kit = ServoKit(channels=16) if ServoKit is not None else None

    backoff = 1
    while True:
        try:
            LOG.info("Connecting to %s", uri)
            async with websockets.connect(uri) as ws:
                LOG.info("Connected to server")
                backoff = 1 # Reset backoff on successful connection

                # Register as the Pi
                await ws.send(json.dumps({"role": "pi"}))
                LOG.info("Sent registration as Pi")

                async for msg in ws:
                    try:
                        data = json.loads(msg)
                        
                        # Validation
                        if not isinstance(data, list) or len(data) != 6:
                            LOG.warning("Unexpected payload format: %s", data)
                            continue
                        
                        numbers = [float(x) for x in data]
                        print("RECV:", numbers)

                        for i, v in enumerate(numbers):
                            kit.servo[15-i].angle = int(v)
                        # Process movement
                        # Pass 'actuate_flag and not dry_run' to determine if physical movement happens
                        await handle_payload(numbers, actuate_flag and not dry_run, kit)

                    except json.JSONDecodeError:
                        LOG.warning("Received invalid JSON: %s", msg)
                    except ValueError:
                        LOG.warning("Payload contains non-numeric values: %s", data)
                    except Exception as e:
                        LOG.error("Error processing message: %s", e)

        except (ConnectionClosedOK, ConnectionClosedError, OSError) as e:
            LOG.warning("Connection lost (%s). Reconnecting in %d seconds...", e, backoff)
        except Exception as e:
            LOG.exception("Unexpected error in listen loop: %s", e)

        await asyncio.sleep(backoff)
        backoff = min(max_backoff, backoff * 2)


def main():
    parser = argparse.ArgumentParser(description="Pi WebSocket client for 6-axis servo control")
    parser.add_argument("--host", required=True, help="Server host IP")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    parser.add_argument("--actuate", action="store_true", help="Enable hardware PWM")
    parser.add_argument("--dry-run", action="store_true", help="Log only, no movement")
    parser.add_argument("--max-backoff", type=int, default=30, help="Max reconnect delay")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    uri = f"ws://{args.host}:{args.port}{WS_PATH}"
    
    try:
        asyncio.run(listen_loop(uri, args.actuate, args.dry_run, args.max_backoff))
    except KeyboardInterrupt:
        LOG.info("Client stopped by user")


if __name__ == "__main__":
    main()