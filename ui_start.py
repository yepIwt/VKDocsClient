from PyQt5 import QtWidgets, uic, QtCore, QtGui, Qt
import sys, os

from core import VKDocsCore
import asyncio

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
		#self.settings_button.clicked.connect(self.get_user_docs)
		self.get_user_docs()

	def contextMenuEvent(self, event):
		#print(self.files.selectedItems()[0].vk_fileinfo)
		contex_menu = QtWidgets.QMenu(self)
		editAction = contex_menu.addAction("Edit")
		action = contex_menu.exec_(self.mapToGlobal(event.pos()))
		if action == editAction:
			print('open edit file ui')

	def run_async_func_fix(self, func, *args, **kwargs):
		loop = asyncio.get_event_loop()
		coroutine = func(*args, **kwargs)
		loop.run_until_complete(coroutine)

	def get_user_docs(self):

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

		if filetype not in self.icons: #gif, pic

			item.setIcon(self.icons['8'])
			
			if preview:
				item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignBottom)
				item.setSizeHint(QtCore.QSize(150, 150) +  QtCore.QSize(10,10))
				item.setIcon(preview)
				item.setFont(QtGui.QFont("Segoe Ui", 9))
		else:
			item.setIcon(self.icons[filetype])

		self.files.addItem(item)
		self.files.setIconSize(QtCore.QSize(120,120))

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	from icons_manager import vk_icons

	token = ""
	vk_upl = VKDocsCore(token)

	window = Ui(vk_icons, vk_upl)
	window.show()
	app.exec_()