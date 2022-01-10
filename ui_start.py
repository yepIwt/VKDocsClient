from PyQt5 import QtWidgets, uic, QtCore, QtGui, Qt
import sys, os

from core import VKDocsCore
from download_core import DownloadUi
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
		self.files.doubleClicked.connect(self.double_clicked)
		self.get_user_docs()


	def contextMenuEvent(self, event):
		contex_menu = QtWidgets.QMenu(self)

		editAction = 0 # fixme
		if len(self.files.selectedItems()) == 1:
			editAction = contex_menu.addAction("Edit")

		deleteAction = contex_menu.addAction("Delete")
		downloadAction = contex_menu.addAction("Download")
		selected_items = self.files.selectedItems()

		action = contex_menu.exec_(self.mapToGlobal(event.pos()))

		if action == deleteAction:
			self.delete_files_from_gui(files = selected_items)
		elif action == editAction:
			self.open_editor(mutableitem = selected_items[0].vk_fileinfo)
		elif action == downloadAction:
			self.menus = []
			for sel_item in selected_items:
				prop = sel_item.vk_fileinfo
				filename = self.core.get_filename_with_ext(prop['filename'], prop['ext'])
				
				self.down_menu = DownloadUi(prop['url'], filename, self.close_downloader)
				self.down_menu.resize(400, 100)
				self.down_menu.show()

	def close_downloader(self):
		self.down_menu.close()

	def double_clicked(self):
		if len(self.files.selectedItems()) >= 1:
			sel_item = self.files.selectedItems()[-1]
			self.open_editor(mutableitem = sel_item.vk_fileinfo)

	def open_editor(self, mutableitem: dict):
		self.editor = edit_file_ui.Ui_Edit_File_Info(
					vk_file_info = mutableitem,
					path_vk_icons = self.icons.path_of_vk_icons
		)
		
		# when editor closed
		self.editor.window_closed.connect(self.edit_file_ui_closed)
		self.editor.show()

	def edit_file_ui_closed(self):
		if self.editor.flag == True: # expl in class
			self.run_async_func_fix(func = self.core.edit_file, **self.editor.mutableFile)
			self.get_user_docs()

	def delete_files_from_gui(self, files: list):
		
		for file_to_delete in files:
			vk_info = file_to_delete.vk_fileinfo
			self.run_async_func_fix(self.core.delete_file, **vk_info)

		self.get_user_docs()

	def run_async_func_fix(self, func, *args, **kwargs):
		loop = asyncio.get_event_loop()
		coroutine = func(*args, **kwargs)
		loop.run_until_complete(coroutine)

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

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	VK_API_DOCS_TOKEN = ""
	cor = VKDocsCore(VK_API_DOCS_TOKEN)
	import vk_icons
	w = Ui(vk_icons, cor)
	w.show()
	sys.exit(app.exec_())