# -*- coding: utf-8 -*- 

from collections import defaultdict
import random
from evaluation import PolicyEvaluation, Q_evaluator
import sys
sys.path.append("..")
from util import modulo

# evaluation de politique en utilisant la difference temporelles
# parametres:
#  max_episodes : nombre maximum d'episodes
#  alpha : taux d'apprentissage
class TD(PolicyEvaluation):

    def __init__(self, *args, **kwargs):
        super(TD, self).__init__(*args)
        self.max_episodes = kwargs.get("max_episodes", 800)
        self.alpha = kwargs.get("alpha", 0.001)

        self.V = defaultdict(lambda:0.0)
        self.Q_evaluator = Q_evaluator(self.environment, lambda state: self.V[state], gamma=self.gamma)

    def evaluate(self):
        self.__generate_episodes_and_evaluate_V()

    def __generate_episodes_and_evaluate_V(self):
       for i in xrange(self.max_episodes):
           self.__generate_episode_and_update_V()

    def __generate_episode_and_update_V(self):
        episode = self.__generate_episode()
        for state, action, next_state in zip(modulo(episode, 2), modulo(episode[1:], 2), modulo(episode[2:], 2)):
            R = self.environment.reward(state, action, next_state)
            self.V[state] = self.V[state] + self.alpha * (R + self.gamma * self.V[next_state] - self.V[state])
 
    def __generate_episode(self):
        starting_state = self.environment.initial_state()
        return self.environment.generate_episode(self.policy, starting_state)

    def evaluate_V(self, state):
        return self.V[state]

    def evaluate_Q(self, state, action):
        return self.Q_evaluator(state, action)
