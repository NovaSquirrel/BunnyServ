#!/usr/bin/env python3
#
# BunnyServ
# Copyright 2023 NovaSquirrel
#
# Copying and distribution of this file, with or without
# modification, are permitted in any medium without royalty
# provided the copyright notice and this notice are preserved.
# This file is offered as-is, without any warranty.
#
import asyncio, time, websockets, json, base64
from aiohttp import web
from config import *

start_time = int(time.time())

authorization_header_value = "Basic "+base64.b64encode((SECRET_USER + ":" + SECRET_PASS).encode()).decode()

# ---------------------------------------------------------

def has_pass(request):
	return request.headers.get("Authorization", None) == authorization_header_value
def dont_have_pass():
	return web.Response(status=401, text="🔨🐇")

# ---------------------------------------------------------

sl_dns_entries = {}

# ---------------------------------------------------------

routes = web.RouteTableDef()
@routes.get('/v1/test')
async def get_test(request):
	return web.Response(text="💚🐇💚")

@routes.get('/v1/time')
async def get_time(request):
	return web.Response(text=str(time.time()))

@routes.get('/v1/sldns')
async def list_dns(request):
	if not has_pass(request):
		return dont_have_pass()
	return web.json_response(list(sl_dns_entries.keys()))

@routes.get('/v1/sldns/{id}')
async def get_dns(request):
	if not has_pass(request):
		return dont_have_pass()
	id = request.match_info['id']
	if id not in sl_dns_entries:
		return web.Response(status=404, text="Not found")
	return web.json_response({"url": sl_dns_entries[id]})

@routes.put('/v1/sldns/{id}')
async def put_dns(request):
	if not has_pass(request):
		return dont_have_pass()
	if not request.can_read_body:
		return web.Response(status=400, text="No body provided")
	id = request.match_info['id']
	sl_dns_entries[id] = await request.text()
	return web.Response(status=200, text="OK!")

@routes.delete('/v1/sldns/{id}')
async def del_dns(request):
	if not has_pass(request):
		return dont_have_pass()
	id = request.match_info['id']
	if id not in sl_dns_entries:
		return web.Response(status=404, text="Not found")
	del sl_dns_entries[id]
	return web.Response(status=200, text="Deleted")

# ---------------------------------------------------------

async def main():
	async with asyncio.TaskGroup() as tg:
		app = web.Application()
		app.add_routes(routes)

		runner = web.AppRunner(app)
		await runner.setup()
		site = web.TCPSite(runner, port=SERVICE_PORT)
		await site.start()

		print("Starting the service!")

		while True:
			await asyncio.sleep(3600)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		print("Shutting the service down...")
	finally:
		pass