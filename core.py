"""
	This is a simple VK Docs client on QT. Use to download and upload your documents
	VKDocsClient, 2021. yepIwt
"""

import os
import aiohttp
import asyncio
from vkwave.api import API
from vkwave.client import AIOHTTPClient

class VKDocsCore:

	def __init__(self, api_key: str):
		api_session = API(tokens = api_key, clients=AIOHTTPClient())
		self.api = api_session.get_context()

	async def upload_file(self, path, filename = None, tags = None):

		vk_api_answer = await self.api.docs.get_upload_server()
		url_for_upload = vk_api_answer.response.upload_url

		if not os.access(path, os.R_OK):
			return (False, 'Bad file')

		f = open(path, 'rb')

		async with aiohttp.ClientSession() as session:
			async with session.post(url_for_upload, data = {'file':f}) as resp:
				json = await resp.json()
				if not json.get('file'):
					raise 'Upload Error'
				file_obj = json['file']

		basename_file = os.path.basename(path)

		await self.api.docs.save(
				file = file_obj,
				title = filename or basename_file,
				tags = tags or None,
		)