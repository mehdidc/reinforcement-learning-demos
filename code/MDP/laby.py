# -*- coding: utf-8 -*- 

from environment import Environment, illegal_state
from policy import Policy, UniformPolicy
import math
import matplotlib.pyplot as plt


class LabyState:
    def __init__(self, coord, id=0):
        self.coord = coord

        x, y = coord
        self.id = id
    
    def __str__(self):
        return str(self.coord)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
       return hash(self.coord)

    def __eq__(self, other):
       return self.coord == other.coord


class Laby(Environment):
    
    def __init__(self, board, *args):
        super(Environment, self).__init__(*args)
        self.board = board
        self.w = len(self.board[0])
        self.h=  len(self.board)

    def valid_actions(self, state):
        x, y = state.coord
        return [action for action in (1, 0), (-1, 0), (0, 1), (0, -1) 
                if self.__in_board((x + action[0], y + action[1])) and 
                   self.__board_value((x + action[0], y + action[1])) != '#']
    
    def initial_state(self):
        for i_lig, lig in enumerate(self.board):
            i_col = lig.find('S')
            if i_col >= 0:
                return LabyState((i_col, i_lig))
        return LabyState((0, 0))

    def valid_states(self, state, action):
        next_state = self.next_state(state, action)
        if next_state is illegal_state:
            return []
        else:
            return [next_state]

    def __in_board(self, coord):
        x, y = coord
        return x >= 0 and y >= 0 and x < self.w and y < self.h
    
    def __board_value(self, coord):
        x, y = coord
        return self.board[y][x]


    def reward(self, state, action, new_state):
        if self.__in_board(new_state.coord) and self.__board_value(new_state.coord) == 'G':
            return 1
        else:
            return -0.1

    def transition(self, state, action, new_state):
        if action in self.valid_actions(state):
            src_x, src_y = state.coord
            action_x, action_y = action
            to_x, to_y = new_state.coord
            if src_x + action_x == to_x and src_y + action_y == to_y:
                return 1.0
            else:
                return 0.0
        else:
            return 0.0
    
    def all_states(self):
        id = 0
        states = []
        for y in xrange(self.h):
            for x in xrange(self.w):
                if self.__board_value((x, y)) != '#':
                    states.append(LabyState((x, y), id=id))
                    id += 1
        return states
    
    def get_number_of_states(self):
        return self.w * self.h
    
    def is_terminal(self, state):
        return True if (self.__board_value(state.coord) == 'G') else False

    def next_state(self, state, action):
        if action in self.valid_actions(state):
            src_x, src_y = state.coord
            action_x, action_y = action
            to_x, to_y = src_x + action_x, src_y + action_y
            return LabyState((to_x, to_y))
        else:
            return illegal_state

def load_board(f):
    board = []
    for line in open(f).readlines():
        line = line[:-1]
        board.append(line)
    return board

board = load_board('laby_example')
laby = Laby(board)

from evaluation.brute import Brute
from evaluation.mc import MonteCarlo 
from evaluation.td import TD
from evaluation.dp import DP
from optimal.mc import MonteCarlo as OpMonteCarlo
from optimal.qlearning import QLearning


def diff_states_values(m1, m2):
    dist = 0.0
    for s in laby.all_states():
        dist += (m1.evaluate_V(s) - m2.evaluate_V(s)) ** 2
    return math.sqrt(dist)

gamma = 0.8

def compare_them():
    policy = UniformPolicy(laby) 
    alpha = 0.001

    mc = MonteCarlo(laby, policy, gamma, max_episodes=1, alpha=alpha)
    mc.evaluate()

    br = Brute(laby, policy, gamma)
    br.evaluate()

    dp = DP(laby, policy, gamma)
    dp.evaluate()
    
    td = TD(laby, policy, gamma, max_episodes=1, alpha=alpha)
    td.evaluate()

    print "Difference entre DP et vraies valeurs", diff_states_values(br, dp)
    
    it = 2000
    epoch = 10
    mc_squared_error = []
    td_squared_error = []
    for i in xrange(it):
        if i % epoch==0:
            mc_squared_error.append(diff_states_values(br, mc))
            td_squared_error.append(diff_states_values(br, td))
        td.evaluate()
        mc.evaluate()
    
    iterations = xrange(1, it + 1, epoch)
    plt.plot(iterations, mc_squared_error, color='blue', label='Monte Carlo')
    plt.plot(iterations, td_squared_error, color='red', label='TD')
    plt.legend(loc='best')
    plt.xlabel('iteration')
    plt.ylabel('Distance euclidienne des valeurs des etats par rapport au vrais valeurs')
    plt.show()

def search_for_optimal():
    policy = UniformPolicy(laby)    
    max_episodes = 200

    mc = OpMonteCarlo(laby, policy, gamma, max_episodes=max_episodes)
    mc.evaluate()

    ql = QLearning(laby, policy, gamma, max_episodes=max_episodes, alpha=0.9, epsilon=0.8)
    ql.evaluate()
    print "Board original : "
    for b in board:
        print b

    def show_policy(meth):
        policy = Policy(laby, meth)
        names = {(1, 0) : 'R', (-1, 0) : 'L', (0, 1) : 'D', (0, -1) : 'U'}
        for y in xrange(laby.h):
            for x in xrange(laby.w):
                state = LabyState((x, y))
                if laby.board[y][x] == '#' or laby.board[y][x] == 'G':
                    print laby.board[y][x],
                else:
                    actions = policy.actions_probas_from(state)
                                   
                    if len(actions) > 0:
                        for action, proba in actions:
                            if proba > 0:
                                print names[action],
                                break
                    else:
                        print ' ',
            print

    print "Solution optimale avec MC"
    show_policy(mc)
    print
    print "Solution optimale avec QL"
    show_policy(ql)


if __name__ == "__main__":
    print "Comparaison entre algorithmes d'evaluation: "
    compare_them()
    print "Chercher la politique optimale: "
    search_for_optimal()
