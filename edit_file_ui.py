from PyQt5 import QtWidgets, uic, QtCore, QtGui, Qt
import sys, os

from core import VKDocsCore
import asyncio

from datetime import datetime

class Ui_Edit_File_Info(QtWidgets.QMainWindow):

	window_closed = QtCore.pyqtSignal()

	def __init__(self, vk_file_info: dict, path_vk_icons):
		super(Ui_Edit_File_Info, self).__init__()
		uic.loadUi('ui/edit_file.ui', self)

		self.mutableFile = vk_file_info
		self.flag = False # IF False user close window Else save

		if self.mutableFile['preview']:
			file_id = str(self.mutableFile['file_id'])
			pixmap = QtGui.QPixmap(f'cachedpreviews/{file_id}.jpg')
		else:
			path_to_icon = path_vk_icons[str(self.mutableFile['type'])]
			pixmap = QtGui.QPixmap(path_to_icon)
		self.preview.setPixmap(pixmap)

		date_from_unixtime = datetime.utcfromtimestamp(self.mutableFile['created']).strftime('%Y-%m-%d %H:%M:%S')
		self.date.setText(date_from_unixtime)

		self.filename.setText(self.mutableFile['filename'])
		
		# Tags list
		self.tableWidget.setColumnCount(2)
		self.tableWidget.setShowGrid(0)
		self.tableWidget.verticalHeader().setVisible(0)
		self.tableWidget.horizontalHeader().setVisible(0)
		self.tableWidget.setShowGrid(0)
		self.add_tag.clicked.connect(self.add_new_tag_from_gui)
		
		for tag in self.mutableFile['tags']:
			self.add_new_tag(tag)

		# Dialog buttons
		self.exit_menu.accepted.connect(self.save)
		self.exit_menu.rejected.connect(self.discard)

	def add_new_tag(self, tagTitle: str):

		self.tableWidget.insertRow(self.tableWidget.rowCount())
		item = QtWidgets.QTableWidgetItem()

		row = self.tableWidget.rowCount() - 1 # fixme

		item.setText(tagTitle)
		item.setTextAlignment(QtCore.Qt.AlignVCenter)

		self.tableWidget.setItem(row,0,item)
		self.tableWidget.resizeColumnsToContents()

		btn_delete = QtWidgets.QPushButton('X')
		btn_delete.setGeometry(200, 150, 100, 40)
		btn_delete.clicked.connect(self.delete_tag)

		self.tableWidget.setCellWidget(row , 1, btn_delete)

	def delete_tag(self):
		button = self.sender()
		tag = self.tableWidget.indexAt(button.pos()).row()
		self.tableWidget.removeRow(tag)
		self.mutableFile['tags'].pop(tag)

	def add_new_tag_from_gui(self):
		new_tag_title = self.new_tag_name.text()
		if new_tag_title:
			item_exist = self.tableWidget.findItems(new_tag_title, QtCore.Qt.MatchExactly)
			if not item_exist:
				self.add_new_tag(new_tag_title)
				self.mutableFile['tags'].append(new_tag_title)

	def save(self):
		self.flag = True
		new_filename = self.filename.text()
		self.mutableFile['filename'] = new_filename
		self.close()

	def discard(self):
		self.flag = False
		self.close()

	def closeEvent(self, event):
		self.window_closed.emit()
		event.accept()