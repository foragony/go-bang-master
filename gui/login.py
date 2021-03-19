from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from client.agent import Agent
from gui.choose_color import ChooseColor


class LogIn(QMainWindow):
	def __init__(self, agent_ip):
		super(LogIn, self).__init__(flags=Qt.WindowFlags())
		self.style = """ 
			QPushButton{background-color:grey;color:white;} 
			#window{ background-image: url(background1.jpg); }
		"""
		self.setStyleSheet(self.style)
		self.agent_ip = agent_ip
		self.server_ip = None
		self.ui = None
		self.ip_input = None
		self.init_ui()

	def init_ui(self):
		self.resize(650, 480)
		self.statusBar().showMessage('Ready')
		self.setObjectName("window")
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
		self.center()

		widget = QWidget()
		label = QLabel()
		label.setText("<font size=%s><B>%s</B></font>" % ("15", "五子棋对战系统"))
		self.ip_input = QLineEdit(self)
		self.ip_input.setPlaceholderText('输入服务器ip')
		connect = QPushButton("connect", self)
		connect.clicked.connect(self.connect_server)
		widget.setStatusTip('  ')
		quit = QPushButton("Quit", self)
		quit.clicked.connect(self.quitClicked)

		# 垂直布局
		vbox1 = QVBoxLayout()
		vbox2 = QVBoxLayout()
		vbox3 = QVBoxLayout()
		vbox4 = QVBoxLayout()

		# 两边空隙填充
		label1 = QLabel()
		label1.resize(50,50)
		label2 = QLabel()
		label2.resize(50, 50)
		vbox1.addWidget(label1)

		vbox4.addWidget(self.ip_input)
		vbox4.addWidget(connect)
		vbox4.addWidget(quit)
		vbox3.addWidget(label2)
		# 按钮两边空隙填充
		label3 = QLabel()
		label3.resize(50, 50)
		label4 = QLabel()
		label4.resize(50, 50)
		hbox1 = QHBoxLayout()
		hbox1.addWidget(label3)
		hbox1.addLayout(vbox4)
		hbox1.addWidget(label4)

		# 标题与两个按钮上下协调
		label5 = QLabel()
		label5.resize(1, 1)
		label6 = QLabel()
		label6.resize(1, 1)
		label7 = QLabel()
		label7.resize(1, 1)
		vbox2.addWidget(label5)
		vbox2.addWidget(label)
		vbox2.addWidget(label6)
		vbox2.addLayout(hbox1)
		vbox2.addWidget(label7)

		hbox = QHBoxLayout()
		hbox.addLayout(vbox1)
		hbox.addLayout(vbox2)
		hbox.addLayout(vbox3)
		widget.setLayout(hbox)

		self.setCentralWidget(widget)

	def connect_server(self):
		text = self.ip_input.text()
		succ = Agent.connect_server(server_ip=text)
		if succ:
			self.hide()
			self.server_ip = text
			# 必须将另一个界面改为成员变量，负责MainPage会与函数调用周期一样一闪而过
			self.ui = ChooseColor(self.agent_ip, self.server_ip)
			self.ui.show()
		else:
			QMessageBox.warning(self, "警告信息", "服务器未开启", QMessageBox.Yes, QMessageBox.Yes)

	def mousePressEvent(self, event):
		if event.button() == Qt.LeftButton:
			self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
			QApplication.postEvent(self, QEvent(174))
			event.accept()

	def mouseMoveEvent(self, event):
		if event.buttons() == Qt.LeftButton:
			self.move(event.globalPos() - self.dragPosition)
			event.accept()

	def quitClicked(self):
		reply = QMessageBox.question(self, 'Warning',
									 'Are you sure to quit?', QMessageBox.Yes,
									 QMessageBox.No)
		if reply == QMessageBox.Yes:
			quit()

	def center(self):
		# 得到该主窗口的矩形框架qr
		qr = self.frameGeometry()
		# 屏幕中间点的坐标cp
		cp = QDesktopWidget().availableGeometry().center()
		# 将矩形框架移至屏幕正中央
		qr.moveCenter(cp)
		# 应用窗口移至矩形框架的左上角点
		self.move(qr.topLeft())
