import math
import random
import simulator
import status, copy
import time
from sys import float_info
from copy import deepcopy
from board import Board, Action
from status import GameStatus, Chess
import logging


class Node(object):
    def __init__(self, status: Board, action=None):
        self.__status = status
        self.__action = action
        self.__total_game = 0
        self.__won_game = 0
        self.__children = []

    def find_best_child(self):
        best_rate, best_node = -1, None
        for i in self.__children:
            if i.__total_game and i.__won_game / i.__total_game > best_rate:
                best_rate = i.__won_game / i.__total_game
                best_node = i
        return best_node

    @property
    def status(self):
        return self.__status

    @property
    def action(self):
        return self.__action

    @property
    def win_prob(self):
        return self.__won_game / self.__total_game \
            if self.__total_game else 0

    def search(self):
        """进行一次mcts搜索"""
        target = status.get_won_status(self.__status.status)
        if self.__children:
            # 如果当前节点已经扩展了，则进行uct选择扩展节点
            node = self.select()
        else:
            # 如果当前节点是根节点，则进行扩展
            self.expand()
            node = self.select()
        if node:
            value = node.playout(target)
            if value is None:
                value = node.search()
            node.update(value)
            return value
        else:
            node.update(None)
            return None


    def print_tree(self, tab=0):
        tab_str = '| ' * (tab - 1) + ('+-' if tab else '')
        print(tab_str + 'won/total: %d/%d' %
              (self.__won_game, self.__total_game),
              end=', ')
        print('action:', str(self.__action), end=', ')
        print('status:', str(self.__status.status))
        for i in self.__children:
            i.print_tree(tab + 1)

    def select(self):
        """uct算法从中选择一个最优项"""
        selected = []
        best_value = -1.0
        for i in self.__children:
            uct = i.__won_game / (i.__total_game + float_info.epsilon)
            uct += math.sqrt(2 * math.log(self.__won_game + 1 + float_info.epsilon)
                             / (i.__total_game + float_info.epsilon))
            uct += 2 + float_info.epsilon
            if uct == best_value:
                selected.append(i)
            if uct > best_value:
                selected = [i]
                best_value = uct
        try:
            return random.choice(selected)
        except IndexError:
            return None
        except TypeError:
            return None


    def expand(self):
        """对当前节点进行扩展，然后再进行通过uct算法选择"""
        if self.__status.won:
            return None
        else:
            if not self.__children:
                actions = simulator.get_all_possible_action(self.__status)
                for action in actions:
                    next_status = copy.deepcopy(self.__status)
                    next_status.apply_action(action)
                    self.__children.append(Node(next_status, action))

    def playout(self, target_status):
        # judge the status
        opposite_status = status.get_opposite(target_status)
        if self.__status.status == target_status:
            return 1  # won the game
        elif self.__status.status == opposite_status:
            return 0  # lost the game
        else:
            return None

    def update(self, value):
        if value is None:
            value = 1
        self.__total_game += 1
        self.__won_game += value

    def apply_action(self, action: Action):
        '''
        博弈中，找到下一步的可行action，然后获得对应的board即可
        '''
        self.expand()
        for child in self.__children:
            if child.__action == action:
                return child
        return None

# some test
if __name__ == '__main__':
    board = Board()
    while True:
        node = Node(board)
        depth = 20 if board.status == GameStatus.RedMoving else 10
        board.apply_action(node.search(depth=depth, breadth=int(depth/4)))
        print(board)
        # node.print_tree()
        try:
            input()
        except KeyboardInterrupt:
            break
        except EOFError:
            break
