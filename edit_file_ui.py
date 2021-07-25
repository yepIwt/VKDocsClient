from PyQt5 import QtWidgets, uic, QtCore, QtGui, Qt
import sys, os

from core import VKDocsCore
import asyncio

from datetime import datetime

class Ui_Edit_File_Info(QtWidgets.QMainWindow):

	def __init__(self, vk_file_info: dict, core_edit_file, path_vk_icons):
		super(Ui_Edit_File_Info, self).__init__()
		uic.loadUi('ui/edit_file.ui', self)

		if vk_file_info['preview']:
			file_id = str(vk_file_info['file_id'])
			pixmap = QtGui.QPixmap(f'cachedpreviews/{file_id}.jpg')
		else:
			path_to_icon = path_vk_icons[str(vk_file_info['type'])]
			pixmap = QtGui.QPixmap(path_to_icon)
		self.preview.setPixmap(pixmap)

		date_from_unixtime = datetime.utcfromtimestamp(vk_file_info['created']).strftime('%Y-%m-%d %H:%M:%S')
		self.date.setText(date_from_unixtime)

		self.filename.setText(vk_file_info['filename'])