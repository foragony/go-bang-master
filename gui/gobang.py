from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtCore
from server.chessboard import ChessBoard
from client.agent import Agent
import time


class Worker(QThread):
	end = pyqtSignal()
	draw_sig = pyqtSignal(int, int, int, name="drawChess")

	def __init__(self, player, chessboard, ai_role):
		super(Worker, self).__init__()
		self.player = player
		self.chessboard = chessboard
		self.is_ai_palyer = ai_role

	def run(self):
		# 游戏对局处于INIT或ACTIVE时
		while self.player.game_status < 2:
			self.player.check_game_status()
			if self.player.my_turn and self.is_ai_palyer:
				xy = self.player.auto_run()
				if xy:
					x, y = xy
					time.sleep(0.3)
					self.player.put_down_chess(x, y)
			for i in range(self.chessboard.board_height):
				for j in range(self.chessboard.board_width):
					self.draw_sig.emit(i, j, self.player.chess_board_status[i][j])
			# 轮询间隔时间
			time.sleep(0.5)
		self.end.emit()


class GoBang(QWidget):
	WIDTH = 540
	HEIGHT = 540
	MARGIN = 22
	GRID = (WIDTH - 2 * MARGIN) / (15 - 1)
	PIECE = 34

	def __init__(self, color, ip, server_ip, ai_role):
		super(GoBang, self).__init__(flags=Qt.WindowFlags())
		self.color = color
		self.step = 0
		self.x, self.y = 1000, 1000
		self.ai_role = ai_role
		# 棋盘类
		self.chessboard = ChessBoard()
		self.pieces = list()
		self.black_img = None
		self.white_img = None
		self.yellow_img = None
		self.mouse_point = None
		self.dialog = None

		self.player = self.player = Agent(server_ip, ip, color)

		self.init_ui(color)
		self.thread = None
		self.work()

	def work(self):
		# 通过信号量控制结束
		self.thread = Worker(self.player, self.chessboard, self.ai_role)
		self.thread.start()
		self.thread.draw_sig.connect(self.draw)
		self.thread.end.connect(self.game_over)

	def init_ui(self, color):
		palette1 = QPalette()  # 设置棋盘背景
		palette1.setBrush(self.backgroundRole(), QtGui.QBrush(QtGui.QPixmap('img/chessboard.jpg')))
		self.setPalette(palette1)
		self.setCursor(Qt.PointingHandCursor)  # 鼠标变成手指形状

		self.resize(GoBang.WIDTH, GoBang.HEIGHT)  # 固定大小 540*540
		self.setMinimumSize(QtCore.QSize(GoBang.WIDTH, GoBang.HEIGHT))
		self.setMaximumSize(QtCore.QSize(GoBang.WIDTH, GoBang.HEIGHT))

		self.setWindowTitle("五子棋")  # 窗口名称
		self.setWindowIcon(QIcon('img/black.png'))  # 窗口图标

		self.black_img = QPixmap('img/black.png')
		self.white_img = QPixmap('img/white.png')
		self.yellow_img = QPixmap('img/yellow.png')

		self.mouse_point = LaBel(self)  # 将鼠标图片改为棋子
		self.mouse_point.setScaledContents(True)

		if color == "black":
			self.mouse_point.setPixmap(self.black_img)  # 加载黑棋
		elif color == "white":
			self.mouse_point.setPixmap(self.white_img)  # 加载白棋
		elif color == "yellow":
			self.mouse_point.setPixmap(self.yellow_img)  # 加载黄棋
		self.mouse_point.setGeometry(270, 270, GoBang.PIECE, GoBang.PIECE)
		# 新建棋子标签，准备在棋盘上绘制棋子
		self.pieces = [LaBel(self) for i in range(self.chessboard.board_width * self.chessboard.board_height)]
		for piece in self.pieces:
			piece.setVisible(True)  # 图片可视
			piece.setScaledContents(True)  # 图片大小根据标签大小可变
		self.mouse_point.raise_()  # 鼠标始终在最上层
		# self.ai_down = True  # AI已下棋，主要是为了加锁，当值是False的时候说明AI正在思考，这时候玩家鼠标点击失效，要忽略掉 mousePressEvent
		self.setMouseTracking(True)
		self.show()

	def paintEvent(self, event):  # 画出指示箭头
		qp = QPainter()
		qp.begin(self)
		self.drawLines(qp)
		qp.end()

	def mouseMoveEvent(self, e):  # 棋子随鼠标移动
		self.mouse_point.move(e.x() - 16, e.y() - 16)

	def mousePressEvent(self, e):  # 玩家下棋
		if not self.player.my_turn:
			return
		# 识别单机动作 同时在AI角色时屏蔽用户点击
		if e.button() == Qt.LeftButton and not self.ai_role:
			x, y = e.x(), e.y()  # 鼠标坐标
			i, j = self.coordinate_transform_pixel_to_map(x, y)  # 对应棋盘坐标
			if i is not None and j is not None:  # 棋子落在棋盘上，排除边缘
				if self.chessboard.get_state_xy(i, j) == ChessBoard.EMPTY:  # 棋子落在空白处
					self.player.put_down_chess(i, j)
					self.draw(i, j, self.player.player_id)
					self.game_over()

	def draw(self, i, j, state):
		x, y = self.coordinate_transform_map_to_pixel(i, j)
		if state == ChessBoard.BLACK:
			self.pieces[i*self.chessboard.board_width+j].setPixmap(self.black_img)  # 放置黑色棋子
		elif state == ChessBoard.WHITE:
			self.pieces[i*self.chessboard.board_width+j].setPixmap(self.white_img)  # 放置白色棋子
		elif state == ChessBoard.YELLOW:
			self.pieces[i*self.chessboard.board_width+j].setPixmap(self.yellow_img)  # 放置黄色棋子
		self.pieces[i*self.chessboard.board_width+j].setGeometry(x, y, GoBang.PIECE, GoBang.PIECE)  # 画出棋子

	def drawLines(self, qp):  # 指示AI当前下的棋子
		if self.step != 0:
			pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
			qp.setPen(pen)
			qp.drawLine(self.x - 5, self.y - 5, self.x + 3, self.y + 3)
			qp.drawLine(self.x + 3, self.y, self.x + 3, self.y + 3)
			qp.drawLine(self.x, self.y + 3, self.x + 3, self.y + 3)

	def coordinate_transform_map_to_pixel(self, i, j):
		# 从 chessMap 里的逻辑坐标到 UI 上的绘制坐标的转换
		return GoBang.MARGIN + j * GoBang.GRID - GoBang.PIECE / 2, GoBang.MARGIN + i * GoBang.GRID - GoBang.PIECE / 2

	def coordinate_transform_pixel_to_map(self, x, y):
		# 从 UI 上的绘制坐标到 chessMap 里的逻辑坐标的转换
		i, j = int(round((y - GoBang.MARGIN) / GoBang.GRID)), int(round((x - GoBang.MARGIN) / GoBang.GRID))
		# 有MAGIN, 排除边缘位置导致 i,j 越界
		if i < 0 or i >= self.chessboard.board_height or j < 0 or j >= self.chessboard.board_width:
			return None, None
		else:
			return i, j

	def refresh_chess_board(self):
		# 游戏对局处于INIT或ACTIVE时
		while self.player.game_status < 2:
			self.player.check_game_status()
			for i in range(self.chessboard.board_height):
				for j in range(self.chessboard.board_width):
					self.draw(i, j, self.player.chess_board_status[i][j])
			# 轮询间隔时间
			time.sleep(1)

	def game_over(self):
		if self.player.winner_id == ChessBoard.EMPTY:
			return
		self.dialog = QMessageBox()
		self.dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		if self.player.winner_id == self.player.player_id:
			reply = QMessageBox.question(self, '你赢了!', '是否继续？', QMessageBox.Yes, QMessageBox.No)
		else:
			reply = QMessageBox.question(self, '很遗憾，你输了！', '是否继续？', QMessageBox.Yes, QMessageBox.No)

		self.player.reset_game()
		self.player.game_status = 0
		if reply == QMessageBox.Yes:  # 复位
			for piece in self.pieces:
				piece.clear()
			self.work()
		else:
			# 退出游戏
			self.player.leave_game()
			self.close()


# ----------------------------------------------------------------------
# 重新定义Label类
# ----------------------------------------------------------------------
class LaBel(QLabel):
	def __init__(self, parent):
		super().__init__(parent)
		self.setMouseTracking(True)

	def enterEvent(self, e):
		e.ignore()
