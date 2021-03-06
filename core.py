"""
	This is a simple VK Docs client on QT. Use to download and upload your documents
	VKDocsClient, 2021. yepIwt
"""

import os
import aiohttp, aiofiles
import asyncio
from vkwave.api import API
from vkwave.client import AIOHTTPClient

class VKDocsCore:

	def __init__(self, api_key: str):
		api_session = API(tokens = api_key, clients=AIOHTTPClient())
		self.api = api_session.get_context()
		self.all_files = []

	async def async_download_by_url(self, url: str) -> bytes:

		async with aiohttp.ClientSession() as session:
			async with session.get(url) as resp:
				file_in_stream = await resp.read()

		await session.close()
		return file_in_stream

	async def async_save_file(self, path_to_save: str, file: bytes) -> None:

		f = await aiofiles.open(path_to_save, 'wb')
		await f.write(file)
		await f.close()

	async def upload_file(self, path, filename = None, tags = None) -> tuple:

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

		return (True,'File Uploaded')

	async def get_all_files(self) -> None:

		self.all_files = []

		vk_api_answer = await self.api.docs.get(return_tags = True)

		for item in vk_api_answer.response.items:
			pic_gif_preview = None
			if item.preview:
				pic_gif_preview = item.preview.photo.sizes[-1].src

			self.all_files.append(
				{
					'file_id': item.id,
					'owner_id': item.owner_id,
					'filename': item.title,
					'created': item.date,
					'type': item.type,
					'ext': item.ext,
					'preview': pic_gif_preview,
					'tags': item.tags,
					'url': item.url,
 				}
			)

	async def download_preview_pic(self, url_to_download: str, file_id: int) -> bool:

		if not os.access('cachedpreviews', os.R_OK):
			try:
				os.mkdir('cachedpreviews')
			except:
				raise 'Error Making Dir'

		file_in_stream = await self.async_download_by_url(url_to_download)

		save_file_to = os.path.join('cachedpreviews', str(file_id) + '.jpg')
		await self.async_save_file(path_to_save = save_file_to, file = file_in_stream)

		return True

	async def get_download_file_info(self, owner_id: int, file_id: int):

		param_docs = "{}_{}".format(owner_id, file_id)

		vk_api_answer = await self.api.docs.get_by_id(docs = param_docs)
		filename = vk_api_answer.response[0].title
		ext = vk_api_answer.response[0].ext
		url_to_download = vk_api_answer.response[0].url

		return filename, ext, url_to_download

	def get_filename_with_ext(self, title: str, ext: str):

		if title[-3:] == ext:
			return title

		title += '.' + ext
		return title

	async def download_file(self, owner_id: int, file_id: int, download_path: str) -> tuple:

		if not os.access(download_path, os.R_OK):
			return (False, 'Error dir')

		filename, _, url_to_download = await get_download_file_info(owner_id, file_id)
		
		file_in_stream = self.async_download_by_url(url_to_download)

		save_file_to = os.path.join(download_path, filename)
		await self.async_save_file(path_to_save = save_file_to, file = file_in_stream)

		return (True, 'File downloaded')

	async def edit_file(self, owner_id: int, file_id: int, filename = None, tags = None, *args, **kwargs) -> tuple:

		param_docs = "{}_{}".format(owner_id, file_id)

		vk_api_answer = await self.api.docs.get_by_id(docs = param_docs, return_tags = 1)

		if not vk_api_answer.response:
			return (False, 'No such file')

		vk_api_answer = await self.api.docs.edit(
			owner_id = owner_id,
			doc_id = file_id,
			title = filename,
			tags = tags,
		)

		if vk_api_answer.response == 1:
			return (True, 'File edited')

		return (False, vk_api_answer.response)

	async def delete_file(self, owner_id: int, file_id: int, *args, **kwargs):

		vk_api_answer = await self.api.docs.delete(owner_id = owner_id, doc_id = file_id)

		if vk_api_answer == 1:
			return (True, 'File deleted')

		return (False, vk_api_answer)