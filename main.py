from PyQt5.QtWidgets import QApplication
from gui.login import LogIn
import sys
import socket


def get_host_ip():
	"""
	查询本机ip地址
	:return:
	"""
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 80))
		ip = s.getsockname()[0]
	except Exception as e:
		print(e)
	finally:
		s.close()

	return ip


if __name__ == '__main__':
	# 可选自动获取IP或者自定义IP
	client_ip = get_host_ip()
	# client_ip = '1.2.3.1'
	app = QApplication(sys.argv)
	ui_login = LogIn(client_ip)
	ui_login.show()
	sys.exit(app.exec_())