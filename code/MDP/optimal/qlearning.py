# -*- coding: utf-8 -*- 

from optimal import OptimalPolicy
import sys
sys.path.append('..')
from evaluation.evaluation import V_evaluator
import random
from collections import defaultdict
from policy import Policy

# cherche la politique optimale en utilisant Qlearning
# parametres:
# - alpha : taux d'apprentissage
# - max_episodes : nombre max d'episodes
# - epsilon : utilise ameliorer l'exploration :  avec une probabilite epsilon on choisit la meilleure action
#             avec une probabilite (1 - epsilon), on choisit une action au hasard.
class QLearning(OptimalPolicy):
    
    def __init__(self, *args, **kwargs):
        super(QLearning, self).__init__(*args)
        
        self.max_episodes = kwargs.get("max_episodes", 200)
        self.alpha = kwargs.get("alpha", 0.9)
        self.Q = defaultdict(lambda:0)
        self.epsilon = kwargs.get("epsilon", 0.8)

       
        self.V_evaluator = V_evaluator(self.environment, 
                                       Policy(self.environment, self.Q), lambda state, action: self.Q[(state, action)])
    
    def evaluate(self):
        for i in xrange(self.max_episodes):
            self.__play_episode()

    def __play_episode(self):
        state = self.environment.initial_state()
        while not self.environment.is_terminal(state):
            actions = self.environment.valid_actions(state)
            
            # greedy epsilon
            rnd = random.random()
            if rnd <= self.epsilon:
                Qs = [self.Q[(state, action)] for action in actions]
                max_Q = max(Qs)
                best_actions = []
                for action, Q in zip(actions, Qs):
                    if Q == max_Q:
                        best_actions.append(action)
                
                best_action = random.choice(best_actions)
            else:
                best_action = random.choice(actions)
            
            next_state = self.environment.next_state(state, best_action)
            R = self.environment.reward(state, best_action, next_state)
            
            actions_next_state = self.environment.valid_actions(next_state)
            if len(actions_next_state):
                max_Q_next_state = max([self.Q[(next_state, action)] for action in actions_next_state])
                self.Q[(state, best_action)] = (self.Q[(state, best_action)] + 
                                                self.alpha * (R + self.gamma * max_Q_next_state - self.Q[(state, best_action)]))
            else:
                break
            state = next_state

    def evaluate_V(self, state):
        return self.V_evaluator(state)

    def evaluate_Q(self, state, action):
        return self.Q[(state, action)]
