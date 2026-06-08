# Raspberry Pi client: listens for 6-number messages and actuates servos.
# Use `--dry-run` to log only without moving hardware.

import asyncio
import json
import logging
import argparse
import time
import sys
import os
from typing import List
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from core.config import SERVER_HOST, SERVER_PORT, SERVO_INDICES, SAFE_POSE, SERVO_MIN_ANGLE, SERVO_MAX_ANGLE
except ImportError:
    logging.error("Could not import core.config. Please ensure you are running this from the c.o.r.i root directory or the client directory.")
    sys.exit(1)

# Third-party imports - websockets for talking, servokit for moving.

# Set up logging so we can see what's happening in the terminal.
LOG = logging.getLogger("pi_client")
WS_PATH = "/ws"
HEARTBEAT_TIMEOUT = 5.0  # Seconds before moving to safe pose if no data is received
# If no messages arrive within HEARTBEAT_TIMEOUT, move to SAFE_POSE

# We check if adafruit_servokit is installed. If not, we run in "dry-run" mode.
# This is super helpful for testing on a laptop without the actual hardware.
try:
    from adafruit_servokit import ServoKit
except ImportError:
    ServoKit = None
    LOG.warning("adafruit_servokit not found. Actuation will be disabled (forced dry-run).")

# This function is where the physical movement happens.
# It takes the joint values and applies them to the servos if we're not in dry-run mode.
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
        
        # Map values to servo indices and set angles
        for i, (v, servo_idx) in enumerate(zip(values, SERVO_INDICES)):
            # Clamp angle to valid servo range
            angle = max(SERVO_MIN_ANGLE, min(SERVO_MAX_ANGLE, int(v)))
            try:
                kit.servo[servo_idx].angle = angle
                LOG.debug("Servo %d (index %s) set to %d°", i, servo_idx, angle)
            except Exception as e:
                LOG.error("Failed to set servo %d to angle %d: %s", i, angle, e)
        LOG.debug("Actuated servos with %s", values)
    else:
        LOG.debug("Payload (dry-run): %s", values)

async def safety_monitor(actuate_flag: bool, kit: 'ServoKit | None', last_msg_time: list):
    """Monitors the heartbeat. If connection is lost or data stops, move to safe pose."""
    moved_to_safe = False
    while True:
        await asyncio.sleep(1.0)
        time_since_last = time.time() - last_msg_time[0]
        
        if time_since_last > HEARTBEAT_TIMEOUT:
            if not moved_to_safe:
                LOG.warning("No data received for %.1fs! Moving to SAFE POSE: %s", time_since_last, SAFE_POSE)
                await handle_payload(SAFE_POSE, actuate_flag, kit)
                moved_to_safe = True
        else:
            moved_to_safe = False

async def listen_loop(uri: str, actuate_flag: bool, dry_run: bool, max_backoff: int):
    """Main WebSocket connection and message handling loop."""
    kit = ServoKit(channels=16) if ServoKit is not None else None
    
    # We use a list to pass by reference to the safety monitor
    last_msg_time = [time.time()]
    
    # Start the safety monitor task
    monitor_task = asyncio.create_task(safety_monitor(actuate_flag and not dry_run, kit, last_msg_time))

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
                        # Update heartbeat timestamp
                        last_msg_time[0] = time.time()
                        
                        data = json.loads(msg)
                        
                        # Validation
                        if not isinstance(data, list) or len(data) != 6:
                            LOG.warning("Unexpected payload format: %s", data)
                            continue
                        
                        numbers = [float(x) for x in data]

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
    parser.add_argument("--host", default=SERVER_HOST, help="Server host IP")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help="Server port")
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