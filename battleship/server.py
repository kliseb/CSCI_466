import argparse
import json
import socket

from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Template
from urllib.parse import parse_qs, urlparse

ATTACKED = [[0 for i in range(10)] for i in range(10)]

HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_NOT_FOUND = 404
HTTP_GONE = 410
HTTP_INTERNAL_SERVER_ERROR = 500

C_REM = 5
B_REM = 4
R_REM = 3
S_REM = 3
D_REM = 2

def get_sink(ship):
    if ship == 'C':
        global C_REM
        C_REM -= 1
        if C_REM == 0:
            return ship
    elif ship == 'B':
        global B_REM
        B_REM -= 1
        if B_REM == 0:
            return ship
    elif ship == 'R':
        global R_REM
        R_REM -= 1
        if R_REM == 0:
            return ship
    elif ship == 'S':
        global S_REM
        S_REM -= 1
        if S_REM == 0:
            return ship
    elif ship == 'D':
        global D_REM
        D_REM -= 1
        if D_REM == 0:
            return ship
    return ''

def process_post(board_file, x, y):
    board = ['']*10
    hit = 0
    sink = ''
    response = {}

    if x < 0 or x > 9 or y < 0 or y > 9:
        response['status'] = HTTP_NOT_FOUND
        return response

    try:
        with open(board_file) as f:
            for i, line in enumerate(f):
                if i == y:
                    global ATTACKED
                    if ATTACKED[x][y] == 1:
                        response['status'] = HTTP_GONE
                        return response
                    ATTACKED[x][y] = 1
                    if line[x] != '_':
                        hit = 1
                        sink = get_sink(line[x])

                        new_line = ''
                        for j, char in enumerate(line):
                            if j == x:
                                new_line += char.lower()
                            else:
                                new_line += char
                        board[i] = new_line
                    else:
                        board[i] = line
                else:
                    board[i] = line
    except FileNotFoundError:
        print('Invalid board file given: {}'.format(board_file))
        return {'status': HTTP_INTERNAL_SERVER_ERROR}

    with open(board_file, 'w') as f:
        for line in board:
            f.write(line)

    response['hit'] = hit
    if sink != '':
        print('Sunk {}'.format(sink))
        response['sink'] = sink
    response['status'] = HTTP_OK
    return response

def build_board(board_file):
    board = [['-' for i in range(10)] for i in range(10)]
    try:
        with open(board_file) as f:
            for i, row in enumerate(f):
                for j, col in enumerate(row):
                    if j < 10:
                        board[i][j] = col
    except FileNotFoundError:
        pass

    title = 'Own Board'
    if board_file == 'opponent_board.txt':
        title = 'Opponent Board'

    with open('board.tmpl') as f:
        template = Template(f.read())
        return template.render(title=title, board=board)

class BattleshipHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            path = urlparse(self.path)
            query = parse_qs(path.query)
            x = int(query['x'][0])
            y = int(query['y'][0])
            print('x: {}, y: {}'.format(x, y))
            response = process_post(own_board, x, y)
            self.send_response(response['status'])
            if response['status'] == HTTP_OK:
                self.send_header("Content-type", "text/html")
                self.end_headers()

                r = r'hit='+str(response['hit'])
                if response.get('sink'):
                    r += r'\&sink='+response['sink']
                self.wfile.write(r.encode('utf-8'))
            else:
                self.end_headers()
        except ValueError:
            self.send_response(HTTP_BAD_REQUEST)
            self.end_headers()

    def do_GET(self):
        response = {}
        build = True
        board = ''
        if self.path in ['/opponent_board.html', '/own_board.html']:
            board = self.path.replace('/', '')
            board = board.replace('.html', '.txt')
            response['status'] = HTTP_OK
        else:
            response['status'] = HTTP_NOT_FOUND
            build = False

        self.send_response(response['status'])
        if response['status'] == HTTP_OK:
            self.send_header('Content-type', 'text/html')
        self.end_headers()
        if build:
            self.wfile.write(build_board(board).encode('utf-8'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    parser.add_argument('board_file', type=str)
    args = parser.parse_args()

    try:
        global own_board
        own_board = args.board_file

        server = HTTPServer(('', int(args.port)), BattleshipHandler)
        print('Started http server on port {}'.format(args.port))
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down the battleship server')
        server.socket.close()

main()
