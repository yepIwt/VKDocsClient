from PyQt5 import QtWidgets, uic, QtCore, QtGui, Qt
import sys, os

from core import VKDocsCore
import asyncio

import edit_file_ui

class Ui(QtWidgets.QMainWindow):

	def __init__(self, vk_icons, vkdocs_object: VKDocsCore):
		super(Ui, self).__init__()
		uic.loadUi('ui/show_files.ui', self)
		self.icons = vk_icons
		self.core = vkdocs_object

		#settings button
		size = QtCore.QSize(40,40)
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap("ui/res/icons/settings.ico"))
		self.settings_button.setIcon(icon)
		self.settings_button.setIconSize(size)
		self.get_user_docs()

	def contextMenuEvent(self, event):
		if len(self.files.selectedItems()) == 1:
			selected_item = self.files.selectedItems()[0]
			contex_menu = QtWidgets.QMenu(self)
			editAction = contex_menu.addAction("Edit")
			action = contex_menu.exec_(self.mapToGlobal(event.pos()))

			if action == editAction:
				self.editor = edit_file_ui.Ui_Edit_File_Info(
					vk_file_info = selected_item.vk_fileinfo,
					path_vk_icons = self.icons.path_of_vk_icons
				)

				# when editor closed
				self.editor.window_closed.connect(self.edit_file_ui_closed)
				self.editor.show()

	def run_async_func_fix(self, func, *args, **kwargs):
		loop = asyncio.get_event_loop()
		coroutine = func(*args, **kwargs)
		loop.run_until_complete(coroutine)

	def edit_file_ui_closed(self):
		if self.editor.flag == True: # expl bellow
			self.run_async_func_fix(func = self.core.edit_file, **self.editor.mutableFile)
			self.get_user_docs()

	def get_user_docs(self):

		self.files.clear()

		self.run_async_func_fix(self.core.get_all_files)

		for file in self.core.all_files:
			preview = None

			if file['preview']:
				# check if preview exist
				chached_filename = str(file['file_id']) + '.jpg'
				chached_filepath = os.path.join('cachedpreviews', chached_filename)

				if not os.access(chached_filepath, os.R_OK):

					self.run_async_func_fix(
						func = self.core.download_preview_pic,
						url_to_download = file['preview'],
						file_id = file['file_id']
					)

				preview = QtGui.QIcon(f"cachedpreviews/{str(file['file_id'])}.jpg")

			self.add_file_to_view(vk_file = file, preview = preview)

	def add_file_to_view(self, vk_file: dict, preview = None):

		filetype, filename = str(vk_file['type']), vk_file['filename']
		item = QtWidgets.QListWidgetItem(filename, self.files)
		item.vk_fileinfo = vk_file

		if filetype not in self.icons.qtobjects: #gif, pic

			item.setIcon(self.icons.qtobjects['8'])
			
			if preview:
				item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
				item.setSizeHint(QtCore.QSize(150, 150) +  QtCore.QSize(10,10))
				item.setIcon(preview)
				item.setFont(QtGui.QFont("Segoe Ui", 9))
		else:
			item.setIcon(self.icons.qtobjects[filetype])

		self.files.addItem(item)
		self.files.setIconSize(QtCore.QSize(120,120))