# -*- coding: utf-8 -*- 

from collections import defaultdict

from evaluation import PolicyEvaluation, Q_evaluator

# evaluation de politique avec l'algorithme de programmation dynamique
# parametres : 
#  max_iter : nombre max d'iterations
#  theta : tolerance
class DP(PolicyEvaluation):
    
    def __init__(self, *args, **kwargs):
        super(DP, self).__init__(*args)
        self.max_iter = kwargs.get("max_iter", 100)
        self.theta = kwargs.get("theta", 0.001)
        self.V = defaultdict(lambda:0.0)
        self.Q_evaluator = Q_evaluator(self.environment, lambda state: self.V[state.id], gamma=self.gamma)
    
    def evaluate(self):
        self.__compute_V_for_all_states()
    
    def __compute_V_for_all_states(self):
        all_states = self.environment.all_states()

        error = None
        it = 0
        while it < self.max_iter and (error is None or error > self.theta):
            error = 0
            for state in all_states:
                V_new = 0.0
                for action in self.environment.valid_actions(state):
                    pi = self.policy(state, action)
                    for state_dst in self.environment.valid_states(state, action):
                        context = state, action, state_dst
                        P = self.environment.transition(*context)
                        R = self.environment.reward(*context)
                        V_new += pi * P * (R + self.V[state_dst.id] * self.gamma)
                error = max(error, abs(V_new - self.V[state.id]))
                self.V[state.id] = V_new
            it += 1
    
    def evaluate_V(self, state):
        return self.V[state.id]

    def evaluate_Q(self, state, action):
        return self.Q_evaluator(state, action)
