# -*- coding: utf-8 -*- 

from optimal import OptimalPolicy
import sys
sys.path.append('..')
from evaluation.mc import MonteCarlo as MonteCarloEvaluation

# cherche la politique optimale en alternant entre MonteCarlo pour l'evaluation de la politique
# et l'algorithme Value Iteration pour l'amelioration de la politique
# parametres:
# - max_episodes : nombre maximum d'episodes
# - max_iterations : nombre de fois ou on alterne entre evaluation et amelioration de politique
class MonteCarlo(OptimalPolicy):
    
    def __init__(self, *args, **kwargs):
        super(MonteCarlo, self).__init__(*args)
        
        self.max_episodes = kwargs.get("max_episodes", 100)
        self.max_iterations = kwargs.get("max_iterations", 10)

        self.best_policy = {}
        policy = lambda state, action: (self.best_policy[(state, action)] 
                                        if (state, action) in self.best_policy else 
                                        self.policy(state, action))
        self.evaluation = MonteCarloEvaluation(self.environment, policy, self.gamma, max_episodes=self.max_episodes)
    
    def evaluate(self):
        for i in xrange(self.max_iterations):
            self. __compute_optimal_Q_for_all_states()

    def __compute_optimal_Q_for_all_states(self):
        self.evaluation.evaluate()
        for state in self.environment.all_states():
            actions = self.environment.valid_actions(state)
            if len(actions):
                Qs = [self.evaluate_Q(state, action) for action in actions]
                max_Q = max(Qs)
                
                nb_maxs = Qs.count(max_Q)
                for action, Q in zip(actions, Qs):
                    if Q == max_Q:
                        self.best_policy[(state, action)] = 1. / nb_maxs
                    else:
                        self.best_policy[(state, action)] = 0.0

    def evaluate_V(self, state):
        return self.evaluation.evaluate_V(state)

    def evaluate_Q(self, state, action):
        return self.evaluation.evaluate_Q(state, action)
