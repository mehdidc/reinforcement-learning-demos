# -*- coding: utf-8 -*- 

from collections import defaultdict
import random
from evaluation import PolicyEvaluation, V_evaluator
import sys
sys.path.append("..")
from util import modulo

# Evaluation de politique en utilisant montecarlo
# parametres:
#  max_episodes : nombre d'episodes
class MonteCarlo(PolicyEvaluation):

    def __init__(self, *args, **kwargs):
        super(MonteCarlo, self).__init__(*args)
        self.max_episodes = kwargs.get("max_episodes", 200)
        self.max_iterations_per_episode = kwargs.get("max_iterations_per_episode", 100)
        self.alpha = kwargs.get("alpha", 1)

        self.Q = defaultdict(lambda:0.0)
        self.V_evaluator = V_evaluator(self.environment, self.policy, lambda state, action: self.Q[(state, action)])
        self.evaluate()
    
    def evaluate(self):
        self.__generate_episodes_and_evaluate_Q()
    
    def __generate_episodes_and_evaluate_Q(self):
       occ_state_action = defaultdict(lambda:0)
       for i in xrange(self.max_episodes):
           self.__generate_episode_and_update_Q(occ_state_action)
    
    def __generate_episode_and_update_Q(self, occ_state_action):
        episode = self.__generate_episode()
        SAS = zip(modulo(episode, 2), modulo(episode[1:], 2), modulo(episode[2:], 2))

        first_occ = {}
        cumulated_R = 0
        cumulated_Rs = []

        cur_gamma = 1
        for i, (state, action, next_state) in enumerate(SAS):
            occ_state_action[(state, action)] += 1
            if (state, action) not in first_occ:
                first_occ[(state, action)] = i
            
            cumulated_R += (self.environment.reward(state, action, next_state)) * cur_gamma
            cumulated_Rs.append(cumulated_R)
            cur_gamma *= self.gamma
        for (state, action), first_occ_i in first_occ.items():
            R_from_first_occ = cumulated_Rs[-1] - (cumulated_Rs[first_occ_i - 1] if first_occ_i >= 1 else 0)
            old_Q = self.Q[(state, action)]
            self.Q[(state, action)] = old_Q + self.alpha * (R_from_first_occ - old_Q) / occ_state_action[(state, action)]

    def __generate_episode(self):
        starting_state = self.environment.initial_state()
        return self.environment.generate_episode(self.policy, starting_state, self.max_iterations_per_episode)

    def evaluate_V(self, state):
        return self.V_evaluator(state)

    def evaluate_Q(self, state, action):
        return self.Q[(state, action)]
