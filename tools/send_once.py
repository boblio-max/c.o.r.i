import asyncio, json, argparse
import websockets

async def main(host, port, values):
    uri = f"ws://{host}:{port}/ws"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps(values, separators=(",", ":")))
        print("sent", values)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True)
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("values", nargs="+", help="6 numbers", type=float)
    args = p.parse_args()
    asyncio.run(main(args.host, args.port, args.values))