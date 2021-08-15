"""
	This file contains UI class that runs donwload
"""

from PyQt5 import QtWidgets, QtGui, QtCore
import os
import sys
import threading
import urllib.request

class Signaller(QtCore.QObject):
    progress_changed = QtCore.pyqtSignal(int)

class DownloadThread(QtCore.QObject):
	
	def __init__(self, url, path):
		super().__init__()
		self.url = url
		self.path = path

	def Handle_Progress(self, blocknum, blocksize, totalsize):
		readed_data = blocknum * blocksize

		if totalsize > 0:
			download_percentage = int(readed_data * 100 / totalsize)

			if download_percentage > 100:
				download_percentage = 100
			self.func_to_emit.emit(download_percentage)

			if download_percentage == 100:
				self.func_to_emit.emit(100)
				self.thread().quit()

	def Download(self,signaller):
		self.func_to_emit = signaller.progress_changed
		urllib.request.urlretrieve(self.url, self.path, self.Handle_Progress)

class DownloadUi(QtWidgets.QMainWindow):

	def __init__(self, download_url: str, filename: str):
		super().__init__()
		self.url = download_url
		self.filename = filename

		self.centralWidget = QtWidgets.QWidget()
		self.setCentralWidget(self.centralWidget)

		btn_start = QtWidgets.QPushButton("Начать загрузку")
		btn_start.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		btn_start.clicked.connect(self.btn_start_clicked)

		self.layout = QtWidgets.QFormLayout(self.centralWidget)

		directory_path = QtWidgets.QLineEdit(self.filename)
		self.btn_choose_dir = QtWidgets.QPushButton('Выбрать директорию')
		self.btn_choose_dir.clicked.connect(self.btn_choose_directory)

		self.layout.addRow(directory_path,self.btn_choose_dir)
		self.layout.addRow(btn_start)

		self.layout.setFormAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

	def btn_choose_directory(self):
		path = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder'))
		self.layout.itemAt(0).widget().setText(path + '/' + self.filename)

	def btn_start_clicked(self):
		status_bar = QtWidgets.QProgressBar()
		self.layout.insertRow(0, "Downloading", status_bar)

		signaller = Signaller()
		signaller.progress_changed.connect(status_bar.setValue)

		path_to_save_file = self.layout.itemAt(0).widget().text()
		download_thread = DownloadThread(self.url, path_to_save_file)

		thread = threading.Thread(
			target=download_thread.Download,
			args=(signaller,),
			daemon=True,
		)
		thread.start()

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	w = DownloadUi('https://gph.is/2K71ZPc','mygif.gif')
	w.resize(400, 100)
	w.show()
	sys.exit(app.exec_())