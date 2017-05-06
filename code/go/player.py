# -*- coding: utf-8 -*- 

from collections import deque, defaultdict
import random
from constants import *

class Player:

    def __init__(self, game_rules, player_color):
        self.game_rules = game_rules
        self.color = player_color

    def get_possible_actions(self):
        board = self.game_rules.board
        all_actions = ((x, y) 
                       for x in xrange(board.dimension[X]) for y in xrange(board.dimension[Y]))
        
        possible_actions = filter(lambda action: self.game_rules.can_do_action(self.color, action), all_actions)
        return possible_actions
    
    def get_next_action(self):
        raise NotImplementedError

class RandomPlayer(Player):

    def get_next_action(self, game):
        possible_actions = self.get_possible_actions()
        if len(possible_actions):
            return random.choice(possible_actions)
        else:
            return noop
 
class DeterministicPlayer(Player):
    
    def __init__(self, actions_seq, *args):
        Player.__init__(self, *args)
        self.actions_seq = actions_seq

    def get_next_action(self, game):
        try:
            next_action =  next(self.actions_seq)
            return next_action
        except StopIteration:
            return noop

class UserInterfacePlayer(Player):
    
    def __init__(self, *args):
        Player.__init__(self, *args)
        self.actions = deque()
   
    def push_action(self, action):
        self.actions.append(action)

    def get_next_action(self, game):
        if len(self.actions):
            return self.actions.popleft()
        else:
            return noop

class StateValueStructure:

    def __init__(self, V=0.):
        self.nb_times_reached = 0
        self.V = V

class MonteCarloPlayer(Player):

    def __init__(self, simulations, depth, *args):
        Player.__init__(self, *args)
        self.simulations = simulations
        self.depth = depth

    def state_value(self, game, depth=0):
        if game.is_end():
            scores = game.get_scores()
            player_score = scores[self.color]
            other_player_score = scores[other(self.color)]
            return player_score - other_player_score
        if depth >= self.depth:
            random_players = {
                    B: RandomPlayer(game.game_rules, B),
                    W: RandomPlayer(game.game_rules, W)
            }
            game.players = random_players

            values = []
            for i in xrange(self.simulations):
                with game.temporary_game():
                    while not game.is_end():
                        game.next_turn()
                        scores = game.get_scores()
                        player_score = scores[self.color]
                        other_player_score = scores[other(self.color)]
                        value = 2*(player_score - other_player_score) + game.nb_prisoners[self.color] - game.nb_prisoners[other(self.color)]
                values.append(value)
            return float(sum(values)) / len(values)
    
        possible_actions = self.get_possible_actions()
        for action in possible_actions:
            with self.game_rules.temporary_do_action(self.color, action):
                game.switch_turn()
                value = self.state_value(game, depth + 1)
                if value != 0:
                    return value
        return 0
    
    def get_next_action(self, game):
        possible_actions = self.get_possible_actions()
        if len(possible_actions) == 0:
            return noop
        actions_values = []
        for action in possible_actions:
            with game.temporary_game():
                game.game_rules.do_action(self.color, action)
                game.switch_turn()
                state_value = self.state_value(game)
                actions_values.append(state_value)
        max_action_value = max(actions_values)
        best_actions = [action for action, value in zip(possible_actions, actions_values) if value==max_action_value]
        return random.choice(best_actions)
