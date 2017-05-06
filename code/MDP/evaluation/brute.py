# -*- coding: utf-8 -*- 

from evaluation import PolicyEvaluation, Q_evaluator
import numpy as np
#from scipy import linalg
from scipy.sparse import linalg, csc_matrix

import time

# la classe "Brute" d'evaluation de politique. les valeurs
# sont evaluees en resolvant le systeme lineaire des equations de bellman directement (en utilisant l'inverse la matrice des coeficients).
class Brute(PolicyEvaluation):
    
    def __init__(self, *args):
        super(Brute, self).__init__(*args)
        self.V = {}
        self.Q_evaluator = Q_evaluator(self.environment, lambda state: self.V[state], gamma=self.gamma)
    
    def evaluate(self):
        self.__compute_V_for_all_states()

    def __compute_V_for_all_states(self):
        all_states = self.environment.all_states()
        coefs = np.zeros((len(all_states), len(all_states)))
        numbers = np.zeros((len(all_states), 1))
        
        for state_src in all_states:
            number = 0.0           
            coefs[state_src.id, state_src.id] = 1
                
            for action in self.environment.valid_actions(state_src):
                pi = self.policy(state_src, action)
                for state_dst in self.environment.valid_states(state_src, action):
                    context = state_src, action, state_dst
                    number += (pi * self.environment.transition(*context) * self.environment.reward(*context))
                    if not self.environment.is_terminal(state_src):
                        coefs[state_src.id, state_dst.id] += -(pi * self.environment.transition(*context) * self.gamma)

            numbers[state_src.id] = number 

        V = linalg.spsolve(csc_matrix(coefs), numbers)
        for state, v in zip(all_states, V):
            self.V[state] = v

    def evaluate_V(self, state):
        return self.V[state]

    def evaluate_Q(self, state, action):
        return self.Q_evaluator(state, action)
