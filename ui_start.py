from PyQt5 import QtWidgets, uic, QtCore, QtGui
import sys


class Ui(QtWidgets.QMainWindow):

	def __init__(self, vk_icons):
		super(Ui, self).__init__()
		uic.loadUi('ui/show_files.ui', self)
		self.icons = vk_icons
		self.files.setIconSize(QtCore.QSize(60,60))

		#settings button
		size = QtCore.QSize(40,40)
		icon = QtGui.QIcon()
		icon.addPixmap(QtGui.QPixmap("ui/res/icons/settings.ico"))
		self.settings_button.setIcon(icon)
		self.settings_button.setIconSize(size)

		for _ in range(100):
			self.add_file_to_view(type = 8, filename = 'lolkek')

	def add_file_to_view(self, type: int, filename: str, preview = None):
		item = QtWidgets.QListWidgetItem(filename, self.files)
		if preview: #gif, pic 
			item.setIcon(self.icons['8'])
		else:
			item.setIcon(self.icons[str(type)])
		self.files.addItem(item)

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	from icons_manager import vk_icons
	window = Ui(vk_icons)
	window.show()
	app.exec_()