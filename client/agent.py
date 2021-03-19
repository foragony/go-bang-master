import requests
import json
import random
from server.chessboard import ChessBoard


class Agent(object):

	SERVER_PORT = 8088

	def __init__(self, server_ip, agent_ip, color):
		self.server_ip = server_ip
		self.agent_ip = agent_ip
		self.color = color
		self.basic_url = "http://{0}:{1}".format(self.server_ip, Agent.SERVER_PORT)

		self.player_id = self.get_agent_id_by_color(color)
		self.game_status = 1
		self.chess_board_status = None
		self.my_turn = False
		self.winner_id = None
		self.board_width = None
		self.board_height = None
		self.chessboard = ChessBoard()

	def start_game(self):
		requests.get(url=self.basic_url + '/rest/play/state?new_state=' + str(self.game_status))

	def check_game_status(self):
		r = requests.get(url=self.basic_url + '/rest/play')
		msg = json.loads(r.text)
		self.my_turn = (msg['current_player'] == self.player_id)
		self.game_status = msg['game_status']
		self.winner_id = msg['winner_player']
		r = requests.get(url=self.basic_url + '/rest/board')
		msg = json.loads(r.text)
		self.chess_board_status = msg['board']
		self.chessboard.set_board(self.chess_board_status)
		self.board_width = int(msg['width'])
		self.board_height = int(msg['height'])

	def put_down_chess(self, x, y):
		"""
		用户下棋请求
		:param x:
		:param y:
		:return: True or False 成功or失败
		"""
		req = {"x": x, "y": y, "player": self.player_id, "color": self.color}
		r = requests.post(url=self.basic_url + '/rest/board', data=json.dumps(req))
		msg = json.loads(r.text)
		return msg['succ']

	def get_agent_id_by_color(self, color):
		r = requests.get(url=self.basic_url + '/rest/player/' + color)
		msg = json.loads(r.text)
		if msg['player_id']:
			return int(msg['player_id'])
		return None

	def reset_game(self):
		r = requests.get(url=self.basic_url + '/rest/play/reset')
		msg = json.loads(r.text)
		return msg['succ']

	def leave_game(self):
		r = requests.post(url=self.basic_url + '/rest/player/exit', data=json.dumps({"color": self.color}))
		msg = json.loads(r.text)
		return msg['succ']

	def auto_run(self):
		if not self.my_turn:
			return
		# 随机走子策略
		# while True:
		# 	i = random.randint(0, self.board_height - 1)
		# 	j = random.randint(0, self.board_width - 1)
		# 	if self.chess_board_status[i][j] == ChessBoard.EMPTY:
		# 		return i, j
		# 初始走子在棋盘中央
		if sum([sum(x) for x in self.chess_board_status]) == 0:
			return self.board_height // 2, self.board_width // 2
		# 最大分数计算策略
		black_player_id = self.get_agent_id_by_color("black")
		white_player_id = self.get_agent_id_by_color("white")
		yellow_player_id = self.get_agent_id_by_color("yellow")
		score_black = [[0 for i in range(self.board_width)] for j in range(self.board_height)]
		score_white = [[0 for i in range(self.board_width)] for j in range(self.board_height)]
		score_yellow = [[0 for i in range(self.board_width)] for j in range(self.board_height)]
		# 计算每一个用户在每个空位走子所能获得的最大分数
		for i in range(self.board_height):
			for j in range(self.board_width):
				if self.chess_board_status[i][j] == ChessBoard.EMPTY:
					score_black[i][j] = self.score(i, j, black_player_id)
					score_white[i][j] = self.score(i, j, white_player_id)
					score_yellow[i][j] = self.score(i, j, yellow_player_id)
		# 转成一维数组方便比较
		score_black_list = []
		for item in score_black:
			score_black_list.extend(item)

		score_white_list = []
		for item in score_white:
			score_white_list.extend(item)

		score_yellow_list = []
		for item in score_yellow:
			score_yellow_list.extend(item)
		# 获取每个位置上的最大得分
		result = [max(a, b, c) for a, b, c in zip(score_black_list, score_white_list, score_yellow_list)]
		# 获取所有位置中得分最大的位置
		chess_index = result.index(max(result))
		# 转换为二维坐标点
		x = chess_index // self.board_height
		y = chess_index % self.board_width
		return x, y

	def score(self, x, y, state):
		"""
		评分算法 计算在（x,y）位置放置state棋子所获得的最大得分
		:param x:
		:param y:
		:param state: 用户
		:return:
		"""
		chess_score = [0, 0, 0, 0]
		# 对米字的4个方向分别检测是否有5子相连的棋
		for idx, directions in enumerate(self.chessboard.dir()):
			chess_score[idx] = 1
			# 对落下的棋子的同一条线的两侧都要检测，结果累积
			for direction in directions:
				point = (x, y)
				# 往指定方向移动一步
				point = self.chessboard.get_xy_direction(point, direction)
				# 获取该位置左侧和右侧各4个连续位置的情况，如果连续同色，chess_score+1 [[左右][左上右下][左下右上][上下]]
				steps = 0
				while point and steps < 4 and 0 <= point[0] <= self.board_height and 0 <= point[1] <= self.board_width:
					# 该位置已有棋子
					if self.chess_board_status[point[0]][point[1]] != ChessBoard.EMPTY:
						# 该位置棋子恰好是当前用户的棋子
						if self.chess_board_status[point[0]][point[1]] == state:
							chess_score[idx] += 1
							steps += 1
							point = self.chessboard.get_xy_direction(point, direction)
						else:
							break
					else:
						break

		# 计算总分
		for score in chess_score:
			# 如果有某个方向超过4，则在此处落子形成五子连珠 直接返回100分的最高分
			if score > 4:
				return 100
		return max(chess_score)

	@staticmethod
	def into_game(agent_ip, server_ip, color):
		req = {"ip": agent_ip, "color": color}
		r = requests.post(url="http://{0}:{1}/rest/player".format(server_ip, Agent.SERVER_PORT), data=json.dumps(req))
		msg = json.loads(r.text)
		return msg['succ'], msg['msg']

	@staticmethod
	def get_player_status(server_ip):
		r = requests.get("http://{0}:{1}/rest/player".format(server_ip, Agent.SERVER_PORT))
		msg = json.loads(r.text)
		return msg

	@staticmethod
	def connect_server(server_ip):
		try:
			r = requests.get("http://{0}:{1}/rest/play".format(server_ip, Agent.SERVER_PORT))
			return True
		except Exception as e:
			print(e)
			return False
