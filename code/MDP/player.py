# -*- coding: utf-8 -*- 

from util import select_using_probability

class Player(object):

    def __init__(self, policy):
        self.policy = policy

    def choose_action(self, state):
        actions_probas = self.policy.actions_probas_from(state)
        if len(actions_probas) == 0:
            return None
        actions, probas = zip(*actions_probas)
        action = select_using_probability(actions, probas)
        return action
