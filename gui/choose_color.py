from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from client.agent import Agent
from gui.gobang import GoBang


class ChooseColor(QMainWindow):
	def __init__(self, agent_ip, server_ip):
		super(ChooseColor, self).__init__(flags=Qt.WindowFlags())
		self.agent_ip = agent_ip
		self.server_ip = server_ip
		self.black_ip_label = None
		self.white_ip_label = None
		self.yellow_ip_label = None
		self.color = None
		self.ui = None
		self.ai_role = None

		self.init_ui()
		self.refresh_clicked()
		self.black_player_ip = None
		self.white_player_ip = None
		self.yellow_player_ip = None

	def init_ui(self):
		self.resize(400, 200)
		self.statusBar().showMessage('Ready')
		self.setObjectName("window")
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
		# self.center()
		widget = QWidget()
		label = QLabel()
		label.setText("<font size=%s><B>%s</B></font>" % ("15", "持方选择"))
		black_label = QLabel()
		black_label.setText("<font size=%s><B>%s</B></font>" % ("10", "黑方"))
		self.black_ip_label = QLabel()
		self.black_ip_label.setText("<font size=%s><B>%s</B></font>" % ("6", "Wait For Client"))
		black_in = QPushButton("加入", self)
		black_in.clicked.connect(lambda: self.player_into_game(self.agent_ip, "black"))
		widget.setStatusTip('  ')
		# start.resize(50, 25)

		white_label = QLabel()
		white_label.setText("<font size=%s><B>%s</B></font>" % ("10", "白方"))
		self.white_ip_label = QLabel()
		self.white_ip_label.setText("<font size=%s><B>%s</B></font>" % ("6", "Wait For Client"))
		white_in = QPushButton("加入", self)
		white_in.clicked.connect(lambda: self.player_into_game(self.agent_ip, "white"))

		yellow_label = QLabel()
		yellow_label.setText("<font size=%s><B>%s</B></font>" % ("10", "黄方"))
		self.yellow_ip_label = QLabel()
		self.yellow_ip_label.setText("<font size=%s><B>%s</B></font>" % ("6", "Wait For Client"))
		yellow_in = QPushButton("加入", self)
		yellow_in.clicked.connect(lambda: self.player_into_game(self.agent_ip, "yellow"))

		start = QPushButton("Start", self)
		start.clicked.connect(self.start_clicked)
		quit = QPushButton("Quit", self)
		quit.clicked.connect(self.quit_clicked)
		refresh = QPushButton("刷新", self)
		refresh.clicked.connect(self.refresh_clicked)

		vbox1 = QVBoxLayout()  # 垂直布局
		vbox2 = QVBoxLayout()
		vbox3 = QVBoxLayout()
		vbox4 = QVBoxLayout()
		vbox5 = QVBoxLayout()
		vbox6 = QVBoxLayout()
		vbox7 = QVBoxLayout()

		# 两边空隙填充
		label1 = QLabel()
		label1.resize(50, 50)
		label2 = QLabel()
		label2.resize(50, 50)
		vbox1.addWidget(label1)

		vbox4.addWidget(black_label)
		vbox4.addWidget(self.black_ip_label)
		vbox4.addWidget(black_in)

		vbox5.addWidget(white_label)
		vbox5.addWidget(self.white_ip_label)
		vbox5.addWidget(white_in)

		vbox7.addWidget(yellow_label)
		vbox7.addWidget(self.yellow_ip_label)
		vbox7.addWidget(yellow_in)

		vbox3.addWidget(label2)
		# 按钮两边空隙填充
		label3 = QLabel()
		label3.resize(100, 50)
		label4 = QLabel()
		label4.resize(100, 50)
		label_y1 = QLabel()
		label_y1.resize(100, 50)
		label_y2 = QLabel()
		label_y2.resize(100, 50)
		hbox1 = QHBoxLayout()
		hbox1.addLayout(vbox4)
		hbox1.addWidget(label3)
		hbox1.addWidget(label4)
		hbox1.addLayout(vbox5)
		hbox1.addWidget(label_y1)
		hbox1.addWidget(label_y2)
		hbox1.addLayout(vbox7)

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

		vbox6.addWidget(refresh)
		vbox6.addWidget(start)
		vbox6.addWidget(quit)
		hbox.addLayout(vbox6)
		widget.setLayout(hbox)

		self.setCentralWidget(widget)

	def refresh_clicked(self):
		msg = Agent.get_player_status(self.server_ip)
		if msg["black_ip"] is not None:
			self.black_ip_label.setText("<font size=%s><B>%s</B></font>" % ("6", msg["black_ip"]))
			if msg["black_ip"] == self.agent_ip:
				self.color = "black"
		else:
			self.black_ip_label.setText("<font size=%s><B>%s</B></font>" % ("6", "Wait For Client"))
		self.black_ip_label.repaint()

		if msg["white_ip"] is not None:
			self.white_ip_label.setText("<font size=%s><B>%s</B></font>" % ("6", msg["white_ip"]))
			if msg["white_ip"] == self.agent_ip:
				self.color = "white"
		else:
			self.white_ip_label.setText("<font size=%s><B>%s</B></font>" % ("6", "Wait For Client"))
		self.white_ip_label.repaint()

		if msg["yellow_ip"] is not None:
			self.yellow_ip_label.setText("<font size=%s><B>%s</B></font>" % ("6", msg["yellow_ip"]))
			if msg["yellow_ip"] == self.agent_ip:
				self.color = "yellow"
		else:
			self.yellow_ip_label.setText("<font size=%s><B>%s</B></font>" % ("6", "Wait For Client"))
		self.yellow_ip_label.repaint()

	def player_into_game(self, player_ip, color):
		succ, msg = Agent.into_game(player_ip, self.server_ip, color)
		if succ:
			reply = QMessageBox.question(self, '选择角色', '是否以AI身份进入？', QMessageBox.Yes, QMessageBox.No)
			if reply == QMessageBox.Yes:
				self.ai_role = True
			else:
				self.ai_role = False
			self.refresh_clicked()
			self.color = color
		else:
			return

	def start_clicked(self):
		self.hide()
		# 必须将另一个界面改为成员变量，否则MainPage会与函数调用周期一样一闪而过
		self.ui = GoBang(self.color, self.agent_ip, self.server_ip, self.ai_role)
		self.ui.show()

	def quit_clicked(self):
		reply = QMessageBox.question(self, '警告', '确定退出？', QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			quit()
