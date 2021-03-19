
# ----------------------------------------------------------------------
# 定义棋盘类，绘制棋盘的形状，切换先后手，判断输赢等
# ----------------------------------------------------------------------


class ChessBoard(object):

	# ----------------------------------------------------------------------
	# 定义棋子类型，输赢情况
	# ----------------------------------------------------------------------
	EMPTY = 0
	BLACK = 1
	WHITE = 2
	YELLOW = 3

	def __init__(self):
		self.board_height = 15
		self.board_width = 15
		self.__board = [[ChessBoard.EMPTY for n in range(self.board_width)] for m in range(self.board_height)]
		self.__dir = [[(-1, 0), (1, 0)], [(0, -1), (0, 1)], [(-1, 1), (1, -1)], [(-1, -1), (1, 1)]]
		#                 (左      右)      (上       下)     (左下     右上)      (左上     右下)

	# 返回数组对象
	def board(self):
		return self.__board

	def dir(self):
		return self.__dir

	def set_board(self, status_matrix):
		self.__board = status_matrix

	def draw_xy(self, x, y, state):
		"""
		在某点放下指定棋子
		:param x:
		:param y:
		:param state:
		:return:
		"""
		self.__board[x][y] = state

	def get_state_xy(self, x, y):
		"""
		获取指定坐标下的状态
		:param x:
		:param y:
		:return:
		"""
		return self.__board[x][y]

	def get_xy_direction(self, point, direction):
		"""
		返回某位置指定方向的位置坐标
		:param point: [x0, y0]
		:param direction: [x_dir, y_dir]
		:return: [x, y] or None
		"""
		x = point[0] + direction[0]
		y = point[1] + direction[1]
		if x < 0 or x >= self.board_width or y < 0 or y >= self.board_height:
			return None
		else:
			return x, y

	def get_xy_direction_status(self, point, direction):
		"""
		返回某位置指定方向的位置坐标的状态
		:param point: [x0, y0]
		:param direction: [x_dir, y_dir]
		:return: state or None
		"""
		if point:
			xy = self.get_xy_direction(point, direction)
			if xy is not None:
				return self.__board[xy[0]][xy[1]]
		return None

	def anyone_win(self, x, y):
		state = self.get_state_xy(x, y)
		for directions in self.__dir:  # 对米字的4个方向分别检测是否有5子相连的棋
			count = 1
			for direction in directions:  # 对落下的棋子的同一条线的两侧都要检测，结果累积
				point = (x, y)
				while True:
					if self.get_xy_direction_status(point, direction) == state:
						count += 1
						point = self.get_xy_direction(point, direction)
					else:
						break
			if count >= 5:
				return state
		return ChessBoard.EMPTY

	def reset(self):
		"""
		重置棋盘
		:return:
		"""
		self.__board = [[ChessBoard.EMPTY for n in range(self.board_width)] for m in range(self.board_height)]