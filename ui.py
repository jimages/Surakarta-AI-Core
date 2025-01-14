import argparse, time
from mcts import Node
from board import Board, Action
from status import GameStatus, Direction
import logging


def read_action(file_name=None):
    # read input
    cmd = input()
    # read from file
    if file_name is not None:
        with open(file_name, 'r') as f:
            cmd = f.readline()
    # parse command
    cmd = cmd.lower().split(' ')
    if cmd[0][0] == 'm':
        dir_dict = {
            'u': Direction.Up,
            'd': Direction.Down,
            'l': Direction.Left,
            'r': Direction.Right,
            'lu': Direction.LeftUp,
            'ld': Direction.LeftDown,
            'ru': Direction.RightUp,
            'rd': Direction.RightDown
        }
        action = Action(int(cmd[1]), int(cmd[2]),
                        direction=dir_dict[cmd[3]])
    elif cmd[0][0] == 'e':
        action = Action(int(cmd[1]), int(cmd[2]),
                        eat_pos=(int(cmd[3]), int(cmd[4])))
    else:
        action = None
    return action


def write_action(node, action, file_name=None):
    print(action)
    print('winning probability: %.2f%%\n' % (100 * node.win_prob))
    if file_name is not None:
        with open(file_name, 'w') as f:
            f.write(str(action))


def print_board(board):
    brd_lines = str(board).split('\n')
    print('  0 1 2 3 4 5')
    for i, j in enumerate(brd_lines):
        print(i, j)
    print()


def ui_main(action_file=None, ai_first=False):
    board = Board()
    action = None
    ai_status = GameStatus.RedMoving if ai_first else GameStatus.BlackMoving
    node = Node(board)
    # main loop
    while not board.won:
        print_board(board)
        if board.status == ai_status:
            time_start = time.time()
            count = 0
            # 在限定时间进行蒙特卡罗模拟
            while((time.time() - time_start) < 30):
                count += 1
                node.search()
            logging.debug("total count %d", count)
            action = node.find_best_child().action
            write_action(node, action, action_file)
        else:
            try:
                action = read_action(action_file)
            except (EOFError, KeyboardInterrupt):
                # end of input
                return
            except:
                action = None
            if action is None:
                print('invalid command')
                continue
        node = node.apply_action(action)
        board = node.status
    print_board(board)
    print('game over', end='')
    if board.status == GameStatus.RedWon:
        print(', red won', end='')
    elif board.status == GameStatus.BlackWon:
        print(', black won', end='')
    print()


if __name__ == '__main__':
    # initialize parser
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(prog='Surakarta MCTS AI')
    parser.formatter_class = argparse.RawTextHelpFormatter
    parser.description = 'An artificial intelligence program that\n' + \
        'can play Surakarta chess implemented by MCTS algorithm.\n' + \
        'Written by MaxXing'
    parser.add_argument('-o', '--output', default=None, type=str,
                        help='output the action that AI took to file')
    parser.add_argument('-af', '--aifirst', default=0, type=int,
                        help='set to 1 if AI should play chess first')
    parser.add_argument('-d', '--depth', default=50, type=int,
                        help='set the search depth of AI')
    parser.add_argument('-b', '--breadth', default=30, type=int,
                        help='set the search breadth of AI')
    # parse arguments
    args = parser.parse_args()
    ui_main(action_file=args.output, ai_first=bool(args.aifirst))
