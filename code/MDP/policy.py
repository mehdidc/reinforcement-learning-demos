# -*- coding: utf-8 -*- 

from collections import defaultdict
from util import select_using_probability

# cette classe definit une politique en se basent sur 
# un environnement et une methode d'evaluation des Q
# Q doit etre un objet qui possed la methode evaluate_Q
class Policy(object):

    def __init__(self, environment, Q):
        self.environment = environment
        self.Q = Q
    
    def actions_probas_from(self, state):
        actions = self.environment.valid_actions(state)
        if len(actions) == 0:
            return []
        
        if callable(self.Q):
            Qs = [self.Q(state, action) for action in actions]
        else:
            Qs = [self.Q.evaluate_Q(state, action) for action in actions]
        max_Q = max(Qs)
        nb_actions = Qs.count(max_Q)
        return [(action, 1./nb_actions if Q==max_Q else 0.0) for action, Q in zip(actions, Qs)]
    
    def choose_action(self, state):
        actions_probas = self.actions_probas_from(state)
        return select_using_probability(*zip(*actions_probas))

    def __call__(self, state, action):
        actions_probas = self.actions_probas_from(state)
        for action_, proba in actions_probas:
            if action == action_:
                return proba
        return 0.0

class UniformPolicy(Policy):

    def __init__(self, environment):
        Q = lambda state, action: 0.
        Policy.__init__(self, environment, Q)

