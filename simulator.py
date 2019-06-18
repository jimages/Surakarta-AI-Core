import random
import copy
import status
from board import Board, Action
from status import Chess, GameStatus, Direction
import logging


def random_action(board: Board):
    """从所有可行操作中进行随机选择"""
    try:
        return random.choice(get_all_possible_action(board))
    except IndexError:
        return None
    except TypeError:
        return None


def get_all_possible_action(board: Board):
    """获得所有的可行action"""
    chess_list = []
    eat_list = []
    actions = []
    # get current chess
    chess = status.get_chess(board.status)
    if chess is None:
        return None
    # 遍历找到当前方可以进行的所以行动
    for y in range(board.board_size):
        for x in range(board.board_size):
            if board.get_chess(x, y) == chess:
                # add current chess to list
                dir_list = board.get_can_move(x, y)
                chess_can_eat = board.get_can_eat(x, y)
                if dir_list:
                    chess_list.append((x, y, dir_list, False))
                if chess_can_eat:
                    eat_list.append((x, y, chess_can_eat, True))
    for x, y, targets, iseat in eat_list + chess_list:
        if iseat:
            actions += [Action(x, y, eat_pos=target) for target in targets]
        else:
            actions += [Action(x, y, direction=target) for target in targets]
    return actions


def simulate(board: Board, target_status):
    # get a copy of board
    b = copy.deepcopy(board)
    # judge the status
    opposite_status = status.get_opposite(target_status)
    # start simulation
    num = 0
    while True:
        action = random_action(b)
        # todo: 存储成树的结构，可以存储下之前模拟的结果
        if b.status == target_status:
            logging.debug("total simulate: %d", num)
            return 1   # won the game
        elif b.status == opposite_status:
            logging.debug("total simulate: %d", num)
            return 0   # lost the game
        num += 1
        if action is None:
            return None
        b.apply_action(action)

# some test
if __name__ == '__main__':
    board = Board()
    first = random_action(board)
    print('first action: move (%d, %d) along %s' % (
        first.x, first.y, first.direction
    ))
    board.apply_action(first)
    print('simulating...')
    total, won = 50, 0
    for _ in range(total):
        won += simulate(board, GameStatus.RedWon)
    print('total games: %d, won games: %d' % (total, won))
    print('win rate: %.2f %%' % ((won / total) * 100))
