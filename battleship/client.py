import argparse
import json
import socket
import urllib3
from urllib.parse import urlencode

OPPONENT_BOARD_FILE = 'opponent_board.txt'

def update_opponent_board(x, y, hit):
    opp_board = ['']*10
    try:
        with open(OPPONENT_BOARD_FILE, 'r') as f:
            for i, line in enumerate(f):
                opp_board[i] = line
    except FileNotFoundError:
        opp_board = ['----------\n' for i in range(10)]

    mark = 'O'
    if hit == 1:
        mark = 'X'
        print('Hit mark: {}'.format(mark))

    replacement = ''
    for index, char in enumerate(opp_board[y]):
        if index == x:
            replacement += mark
        else:
            replacement += char
    opp_board[y] = replacement

    with open(OPPONENT_BOARD_FILE, 'w') as f:
        for line in opp_board:
            f.write(line)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str)
    parser.add_argument('port', type=int)
    parser.add_argument('x', type=int)
    parser.add_argument('y')#, type=int)
    args = parser.parse_args()

    http = urllib3.HTTPConnectionPool(args.host, args.port)
    encoded_args = urlencode({'x': args.x, 'y': args.y})
    url = 'http://'+args.host+':'+str(args.port)+'/?'+encoded_args
    r = http.request('POST', url)

    data = r.data.decode('utf-8')
    hit = 0
    sink = ''
    print(r.status)
    if r.status == 200:
        split = data.split('=')
        if len(split[1]) > 1:
            hit = int(split[1][0])
            sink = split[2]
        else:
            hit = int(split[1])
        update_opponent_board(args.x, int(args.y), hit)

        print('Hit: {}'.format(hit))
        if sink != '':
            print('Sink: {}'.format(sink))

main()
