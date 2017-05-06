
# classe mere des classes qui trouvent les actions optimales
class OptimalPolicy(object):
    def __init__(self, environment, initial_policy, gamma=0.5):
        self.environment = environment
        self.policy = initial_policy
        self.gamma = gamma
    
    def evaluate(self):
        pass

    def evaluate_V(self):
        pass

    def evaluate_Q(self):
        pass

    def get_all_V(self):
        return dict((state, self.evaluate_V(state)) for state in self.environment.all_states())

    def get_all_Q(self):
        return dict(((state, action), self.evaluate_Q(state, action))
                for state in self.environment.all_states() 
                for action in self.environment.valid_actions(state))
