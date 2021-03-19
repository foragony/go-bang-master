from flask import Flask
from flask.globals import request
from flask_cors import CORS
from server.chessboard import ChessBoard
from server.game import Game
from client.agent import Agent
import json


app = Flask(__name__)
CORS(app, supports_credenials=True)
game_server = None

"""
当前棋局管理
"""


@app.route('/rest/play', methods=['GET'])
def get_game_status_svc():
    return json.dumps({
        "game_status": game_server.game_status,
        "current_player": game_server.current_player,
        "winner_player": game_server.win_player
    })


@app.route('/rest/play/state', methods=['GET'])
def set_game_status_svc():
    value = request.args.get('new_state', -1)
    value = int(value)
    if value > 0:
        game_server.game_status = value
        succ = True
    else:
        succ = False
    return json.dumps({
        "succ": succ
    })


@app.route('/rest/play/reset', methods=['GET'])
def reset_game_svc():
    try:
        game_server.reset()
        succ = True
    except Exception as e:
        print(e)
        succ = False
    return json.dumps({
        "succ": succ
    })


@app.route('/rest/play/report', methods=['GET'])
def get_game_report_svc():
    return json.dumps({
        "report": "这是一份棋局报告，内容待定！"
    })


"""
玩家管理
"""


@app.route('/rest/player', methods=['GET', 'POST'])
def player_svc():
    if request.method == 'GET':
        return json.dumps({
            "black_ip": None if game_server.black_player is None else game_server.black_player.agent_ip,
            "white_ip": None if game_server.white_player is None else game_server.white_player.agent_ip,
            "yellow_ip": None if game_server.yellow_player is None else game_server.yellow_player.agent_ip
        })
    elif request.method == 'POST':
        msg = json.loads(request.get_data())
        player_ip = msg['ip']
        color = msg['color']
        succ = True

        # 不允许同一IP多次加入游戏
        already_into_ips = set()
        if game_server.black_player:
            already_into_ips.add(game_server.black_player.agent_ip)
        if game_server.white_player:
            already_into_ips.add(game_server.white_player.agent_ip)
        if game_server.yellow_player:
            already_into_ips.add(game_server.yellow_player.agent_ip)
        if player_ip in already_into_ips:
            succ = False
            msg = "您已经加入该棋局"
        elif color == "black" and game_server.black_player is None:
            game_server.black_player = Agent(sever_ip, player_ip, color)
            msg = '黑方成功加入棋局'
        elif color == "white" and game_server.white_player is None:
            game_server.white_player = Agent(sever_ip, player_ip, color)
            msg = '白方成功加入棋局'
        elif color == "yellow" and game_server.yellow_player is None:
            game_server.yellow_player = Agent(sever_ip, player_ip, color)
            msg = '黄方成功加入棋局'
        else:
            succ = False
            msg = '用户{0}加入棋局失败'.format(player_ip)
        return json.dumps({
            "succ": succ,
            "msg": msg
        })


@app.route('/rest/player/exit', methods=['POST'])
def leave_game():
    msg = json.loads(request.get_data())
    color = msg['color']
    succ = True
    if color == "black":
        game_server.black_player = None
    elif color == "white":
        game_server.white_player = None
    elif color == "yellow":
        game_server.yellow_player = None
    else:
        succ = False
    return json.dumps({"succ": succ})


@app.route('/rest/player/<color>', methods=['GET'])
def get_player_status_svc(color):
    if color == 'black':
        player_id = ChessBoard.BLACK
    elif color == 'white':
        player_id = ChessBoard.WHITE
    elif color == 'yellow':
        player_id = ChessBoard.YELLOW
    else:
        player_id = None
    return json.dumps({
        "player_id": player_id
    })


"""
当前棋盘管理
"""


@app.route('/rest/board', methods=['GET', 'POST'])
def chess_board_svc():
    if request.method == 'GET':
        return json.dumps(
            {
                "board": game_server.game_board.board(),
                "width": game_server.game_board.board_width,
                "height": game_server.game_board.board_height
            }
        )
    elif request.method == 'POST':
        msg = json.loads(request.get_data())
        player = msg["player"]
        x = msg["x"]
        y = msg["y"]
        if player in {ChessBoard.BLACK, ChessBoard.WHITE, ChessBoard.YELLOW}:
            ret_code = game_server.put_down_chess(x, y, player)
            if ret_code >= 0:
                succ = True
                msg = "下棋成功"
            elif ret_code == -1:
                succ = False
                msg = "该位置已有棋子，请更换位置"
            else:
                succ = False
                msg = "请等待其他用户下棋"
            return json.dumps({
                "succ": succ,
                "msg": msg
            })
        else:
            return json.dumps({
                "succ": False,
                "msg": "该用户不在棋局内"
            })


if __name__ == '__main__':
    game_server = Game()
    sever_ip = '127.0.0.1'
    app.run(
        host='0.0.0.0',
        port='8088',
        debug=True
    )