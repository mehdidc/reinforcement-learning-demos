# -*- coding: utf-8 -*- 

from util import select_using_probability, modulo

illegal_state = None
# Cette classe determine toutes les caratertisiques necessaires
# pour definir un environnement.
# Elle doit etre heritee pour creer un environnement specifique.
class Environment(object):

    def valid_actions(self, state):
        return []
    
    def valid_states(self, state, action):
        return []

    def reward(self, state, action, new_state):
        return 0

    def transition(self, state, action, new_state):
        return 0.0
    
    def all_states(self):
        return []
    
    def get_number_of_states(self):
        return 0

    def is_terminal(self, state):
        return False

    def next_state(self, state, action):
        return illegal_state
    
    def generate_episode(self, policy, starting_state, max_iterations=None):
        state = starting_state
        episode = [state]
        it = 0
        while (max_iterations is not None and it < max_iterations) or (max_iterations is None):
            actions = self.valid_actions(state)
            probabilities = [policy(state, action) for action in actions]
            action =  select_using_probability(actions, probabilities)
            episode.append(action)
            next_state = self.next_state(state, action)
            episode.append(next_state)
            if self.is_terminal(next_state):
                break
            else:
                state = next_state
            it += 1
        return episode
    
    def episode_rewards(self, episode):
        for state, action, next_state in zip(modulo(episode, 2), modulo(episode[1:], 2), modulo(episode[2:], 2)):
            R = self.reward(state, action, next_state)
            yield R

    def initial_state(self):
        pass
