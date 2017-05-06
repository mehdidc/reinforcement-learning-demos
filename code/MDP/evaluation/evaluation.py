# cette classe est la classe mere des classes d'evaluations de politques
class PolicyEvaluation(object):

    def __init__(self, environment, policy, gamma=0.5):
        self.environment = environment
        self.policy = policy
        self.gamma = gamma
    
    def evaluate(self):
        pass

    def evaluate_V(state):
        pass
    
    def evaluate_Q(state, action):
        pass
    
    def get_all_V(self):
        return [self.evaluate_V(state) for state in self.environment.all_states()]

    def get_all_Q(self):
        return [self.evaluate_Q(state, action) for state in self.environment.all_states() for action in self.environment.valid_actions(state)]

def Q_evaluator(environment, V_evaluator, gamma=0.5):

    def evaluator(state, action):
        Q = 0.0
        for state_dst in environment.valid_states(state, action):
            context = state, action, state_dst
            P = environment.transition(*context)
            R = environment.reward(*context)
            Q += P * (R + V_evaluator(state_dst) * gamma)
        return Q
    return evaluator

def V_evaluator(environment, policy, Q_evaluator):

    def evaluator(state):
        V = 0.0
        for action in environment.valid_actions(state):
            pi = policy(state, action)
            V += pi * Q_evaluator(state, action)
        return V
    return evaluator
