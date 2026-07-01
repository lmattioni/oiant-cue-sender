#!/usr/bin/env python3
"""
OIANT Cue Sender — Servidor cloud
HTTP + WebSocket en el mismo puerto via asyncio
"""
import asyncio, os, json
from aiohttp import web
import aiohttp

clients = set()
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "OIANT_CueSender.html")

async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    clients.add(ws)
    print(f"+ Conectado  ({len(clients)} activos)")
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                targets = [c for c in clients if c is not ws]
                await asyncio.gather(
                    *[c.send_str(msg.data) for c in targets],
                    return_exceptions=True
                )
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break
    finally:
        clients.discard(ws)
        print(f"- Desconectado  ({len(clients)} activos)")
    return ws

async def index(request):
    try:
        with open(HTML_FILE, 'rb') as f:
            content = f.read()
        return web.Response(body=content, content_type='text/html', charset='utf-8')
    except FileNotFoundError:
        return web.Response(text="OIANT_CueSender.html no encontrado", status=404)

async def health(request):
    return web.Response(text="OK")

app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", ws_handler)
app.router.add_get("/health", health)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Servidor corriendo en puerto {port}")
    web.run_app(app, host="0.0.0.0", port=port)
