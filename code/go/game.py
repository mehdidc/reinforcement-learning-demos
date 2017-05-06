# -*- coding: utf-8 -*- 

from contextlib import contextmanager
from constants import *
from board import Board
from player import RandomPlayer, MonteCarloPlayer
from collections import deque

class GameRules:

    def __init__(self, board):
        self.board = board
        self.last_board_hashes = deque(maxlen=3)
    
    def can_do_action(self, player, action):

        if action == noop:
            return True

        if not self.board.inside(action):
            return False

        if self.board.content(action) != E:
            return False
       
        with self.temporary_do_action(player, action):
            chaine = self.board.chaine_starting_from(player, action)
            if self.board.liberte_groupe(chaine) == 0:
                return False
            if len(self.last_board_hashes) == 3 and self.last_board_hashes[0] == self.last_board_hashes[2]:
                return False

        return True
    
    def get_action_prisoners(self, player, action):
        # assume that the action can be performed

        with self.board.temporary_replace_with([action], player):
            prisoners = []
            chaines = self.board.chaines(other(player))
            for chaine in chaines:
                if self.board.liberte_groupe(chaine) == 0:
                    prisoners.extend(chaine)
            return prisoners

    def do_action_and_get_nb_prisoners(self, player, action):
        # assume that the action can be performed
        self.last_board_hashes.append(hash(self.board))
        prisoners = self.get_action_prisoners(player, action)
        self.board.replace_with(prisoners, E)
        self.board.replace_with([action], player)

        return len(prisoners)
    
    def do_action(self, player, action):
        # assume that the action can be performed
        
        self.do_action_and_get_nb_prisoners(player, action)
    
    def save(self):
        return (self.board.get_content(), list(self.last_board_hashes))

    def load(self, data):
        board_content, last_board_hashes = data
        self.board.load_content(board_content)
        self.last_board_hashes = deque(last_board_hashes, maxlen=3)

    @contextmanager
    def temporary_do_action(self, player, action):
        data = self.save()
        self.do_action(player, action)
        yield self
        self.load(data)
    
class Game:

    def __init__(self, game_rules, players, starting_player=B):
        self.game_rules = game_rules
        self.turn = starting_player
        self.players = players
        self.nb_prisoners = {W: 0, B: 0}
        self.actions_history = {W: [], B: []}
    
    def save(self):
        old_rules = self.game_rules.save()
        old_turn = self.turn
        
        old_players = {}
        old_players.update(self.players)

        old_nb_prisoners = {}
        old_nb_prisoners.update(self.nb_prisoners)
        
        old_actions_history = {}
        old_actions_history.update(self.actions_history)
        return old_rules, old_turn, old_players, old_nb_prisoners, old_actions_history

    def load(self, data):
        rules, turn, players, nb_prisoners, actions_history = data
        self.game_rules.load(rules)
        self.turn = turn
        self.players = players
        self.nb_prisoners = nb_prisoners
        self.actions_history = actions_history

    @contextmanager
    def temporary_game(self):
        data = self.save()
        yield self
        self.load(data)
    
    def switch_turn(self):
        self.turn = other(self.turn)

    def next_turn(self):
        #print "Turn of " + str(self.turn)
        player = self.players[self.turn]
        action = player.get_next_action(self)

        #print "Trying action " + str(action)
        if not self.game_rules.can_do_action(player.color, action):
            action = noop

        if action == noop:
            pass
            #print "Pass !"
        else: 
            prisoners = self.game_rules.get_action_prisoners(self.turn, action)
            nb_prisoners = len(prisoners)

            self.game_rules.do_action(self.turn, action)
            
            self.nb_prisoners[player.color] += nb_prisoners
            #if nb_prisoners:
            #    print "Prisoners : " + str(nb_prisoners) + " at " + str(prisoners)
        
        self.actions_history[self.turn].append(action)
        self.switch_turn()

    def is_end(self):
        if len(self.actions_history[W]) == 0 or len(self.actions_history[B]) == 0:
            return False
        else:
            if self.actions_history[W][-1] == noop and self.actions_history[B][-1] == noop:
                return True
            elif self.actions_history[W][-1] == noop and self.game_rules.board.count(W)==0 and self.turn==B:
                return True
            elif self.actions_history[B][-1] == noop and self.game_rules.board.count(B)==0 and self.turn==W:
                return True
            else:
                return False

    def get_scores(self):
       scores = {}
       for player in (W, B):
           player_score = 0
           
           territoires = self.game_rules.board.territoires(player)
           player_score += sum(len(territoire) for territoire in territoires)
           
           player_score += self.game_rules.board.count(player)

           scores[player] = player_score
       return scores

def duel(rules, players, nb_games):
    scores = {W: 0, B: 0}
    for starting_player in B, W:
        for g in xrange(nb_games):
            rules.board.clear()
            game  = Game(rules, players, starting_player=starting_player)
            while not game.is_end():
                print "Turn of %s" % (game.turn,)
                game.next_turn()
                action = game.actions_history[other(game.turn)][-1]
                print "%s plays %s" % (other(game.turn), action)
            print "End of the game"
            s = game.get_scores()
            scores[W] += s[W]
            scores[B] += s[B]
    scores[W] = float(scores[W]) / (2*nb_games)
    scores[B] = float(scores[B]) / (2*nb_games)
    return scores 

if __name__ == "__main__":
    b = Board((4, 4))
    rules = GameRules(b)
    nb_plays = 5
    # Duel entre deux Monte Carlo Player avec (nbr simulations = 1) pour W et (nbr simulations = 2) pour B
    players = {
            W:MonteCarloPlayer(1, 1, rules, W),
            B:MonteCarloPlayer(1, 2, rules ,B)
    }
    scores1 = duel(rules, players, nb_plays)

    players = {
            B:MonteCarloPlayer(1, 1, rules, B),
            W:RandomPlayer(rules , W)
    }
    scores2 = duel(rules, players, nb_plays)

    players = {
            B:MonteCarloPlayer(2, 2, rules, B),
            W:RandomPlayer(rules , W)
    }
    scores3 = duel(rules, players, nb_plays)

    print "%d jeux joués pour chaque cas, %d avec le premier joueur qui commence, %d avec le deuxieme qui commence" % (nb_plays*2, nb_plays, nb_plays)
    print "Deux Monte Carlo (profondeur=1, couleur=W) pour le premier, (profondeur=2, couleur=B) pour le deuxieme, nbr_simulations=1 pour les deux"
    print scores1

    print "Monte Carlo (couleur=B, profondeur=1, nbr_simulations=1) et Random(couleur=W)"
    print scores2

    print "Monte Carlo (couleur=B, profondeur=2, nbr_simulations=2) et Random(couleur=W)"
    print scores3
