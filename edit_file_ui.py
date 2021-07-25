from PyQt5 import QtWidgets, uic, QtCore, QtGui, Qt
import sys, os

from core import VKDocsCore
import asyncio

from datetime import datetime

class Ui_Edit_File_Info(QtWidgets.QMainWindow):

	def __init__(self, vk_file_info: dict, core_edit_file, path_vk_icons):
		super(Ui_Edit_File_Info, self).__init__()
		uic.loadUi('ui/edit_file.ui', self)

		self.mutableFile = vk_file_info

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
		
		self.tableWidget.setColumnCount(2)
		self.tableWidget.setShowGrid(0)
		self.tableWidget.verticalHeader().setVisible(0)
		self.tableWidget.horizontalHeader().setVisible(0)
		self.tableWidget.setShowGrid(0)
		#Tags 
		for tag in self.mutableFile['tags']:
			self.add_new_tag(tag)

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