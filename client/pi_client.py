# C.O.R.I Raspberry Pi Client
# This script runs on the actual Pi. It listens for commands from the server
# and then tells the servos exactly how to move. It's the robot's nervous system!

import asyncio
import json
import logging
import argparse
from typing import List

# Third-party imports - websockets for talking, servokit for moving.
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

# Set up logging so we can see what's happening in the terminal.
LOG = logging.getLogger("pi_client")
WS_PATH = "/ws"

# We check if adafruit_servokit is installed. If not, we run in "dry-run" mode.
# This is super helpful for testing on a laptop without the actual hardware.
try:
    from adafruit_servokit import ServoKit
except ImportError:
    ServoKit = None
    LOG.warning("adafruit_servokit not found. Actuation will be disabled.")

<<<<<<< Updated upstream
# Servo channel mapping
# Adjust these indices based on your servo setup
SERVO_MAP = {
    'base': 11,          # A1: Base rotation
    'shoulder': 12,      # A2: Shoulder
    'elbow': 13,         # A3: Elbow
    'wrist': 14,         # A4: Wrist
    'claw': 15,          # Claw/Grabber
    'spare': 10          # Extra servo
}

SERVO_INDICES = [
    SERVO_MAP['base'],
    SERVO_MAP['shoulder'],
    SERVO_MAP['elbow'],
    SERVO_MAP['wrist'],
    SERVO_MAP['claw'],
    SERVO_MAP['spare']
]


=======
# This function is where the physical movement happens.
# It takes the joint values and applies them to the servos if we're not in dry-run mode.
>>>>>>> Stashed changes
async def handle_payload(values: List[float], actuate: bool, kit: 'ServoKit | None'):
    """
    Handles the actual movement of servos based on received values.
    
    Args:
        values: List of 6 servo angles [base, shoulder, elbow, wrist, claw, spare]
        actuate: Whether to actually move servos (True) or just log (False)
        kit: ServoKit instance (None if not available)
    """
    if len(values) != 6:
        LOG.warning("Received payload with wrong length: %s", values)
        return

    if actuate:
        if kit is None:
            LOG.error("Actuation requested but ServoKit is not initialized")
            return
        
<<<<<<< Updated upstream
        # Map values to servo indices and set angles
        for i, (v, servo_idx) in enumerate(zip(values, SERVO_INDICES)):
            # Clamp angle to valid servo range (0-180)
=======
        # Map values to servo angles (clamped between 0 and 180 degrees).
        for i, v in enumerate(values):
>>>>>>> Stashed changes
            angle = max(0, min(180, int(v)))
            try:
                kit.servo[servo_idx].angle = angle
                LOG.debug("Servo %d (index %s) set to %d°", i, servo_idx, angle)
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

                # We have to tell the server that we are the Pi so it knows where to send data.
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