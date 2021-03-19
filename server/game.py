"""
游戏对局类
"""
from server.chessboard import ChessBoard

INIT = 0  # 尚未开始
ACTIVE = 1  # 已开始
IDLE = 2  # 空闲
OVER = 3  # 对局结束


class Game(object):

	def __init__(self):
		self.current_player = ChessBoard.BLACK
		self.game_status = INIT
		self.win_player = ChessBoard.EMPTY
		self.game_board = ChessBoard()
		self.black_list = []  # 黑棋落子记录
		self.white_list = []  # 白棋落子记录
		self.yellow_list = []  # 黄棋落子记录

		self.black_player = None  # 黑棋用户
		self.white_player = None  # 白棋用户
		self.yellow_player = None  # 黄棋用户

	def put_down_chess(self, x, y, player):
		if player == self.current_player:
			if self.game_board.get_state_xy(x, y) == ChessBoard.EMPTY:
				# 修改棋盘状态
				self.game_board.draw_xy(x, y, player)
				# 记录下棋历史
				self.add_move_record(x, y, player)
				# 用户转到下一个
				self.next_player()
				if self.game_board.anyone_win(x, y) > 0:
					self.win_player = self.game_board.anyone_win(x, y)
					self.game_status = OVER
					print("game over")
					return 1
				else:
					return 0
			else:
				print("该位置已有棋子，请更换位置")
				return -1
		else:
			print("请等待其他用户下棋")
			return -2

	def get_current_player(self):
		return self.current_player

	def next_player(self):
		if self.current_player == ChessBoard.BLACK:
			self.current_player = ChessBoard.WHITE
		elif self.current_player == ChessBoard.WHITE:
			self.current_player = ChessBoard.YELLOW
		else:
			self.current_player = ChessBoard.BLACK

	def add_move_record(self, x, y, player):
		if player == ChessBoard.BLACK:
			self.black_list.append((x, y))
		elif player == ChessBoard.WHITE:
			self.white_list.append((x, y))
		else:
			self.yellow_list.append((x, y))

	def reset(self):
		self.current_player = ChessBoard.BLACK
		self.game_status = INIT
		self.win_player = ChessBoard.EMPTY
		self.game_board = ChessBoard()
		self.black_list = []  # 黑棋落子记录
		self.white_list = []  # 白棋落子记录
		self.yellow_list = []  # 黄棋落子记录