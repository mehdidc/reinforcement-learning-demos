# -*- coding: utf-8 -*- 

# Quatres méthodes : greddy, greedy epsilon, softmax et ucb
# chaque méthode est une fonction qui reçoit deux arguments :
# approx_Qs : la liste des retours moyens de chaque machine à l'itération courante
# iteration : indice de l'itération courante

import random
import math

# simule un jeu du bandit.
# real_Qs : la liste des vraies valeurs des machines
# tries : nombre d'essais
# sel_action : la fonction à utiliser pour selectionner l'action.
#              trois méthodes sont proposées : greedy, greedy-epsilon, softmax
def simulate(real_Qs, tries, sel_action, updated_Q):
    approx_Qs = len(real_Qs) * [0.] # les valeurs approchées des real_Qs
    times = len(real_Qs) * [0] # nombre de fois où on selectionne chaque machine
    
    rewards = []
    actions = []
    for i in xrange(tries):
        # pour chaque essai :
        action = sel_action(approx_Qs, iteration=i) # selectionner d'abord l'action (càd la machine selectionnée)
        actions.append(action)

        reward = action_reward(real_Qs[action]) # puis, observer le gain
        rewards.append(reward)

        times[action] += 1
        # ensuite mettre à jour la valeur approchée de real_Qs de la machine selectionnée
        approx_Qs[action] = updated_Q(approx_Qs[action],
                                      times[action],
                                      reward)
    return Result(rewards, actions)

class Result:

    def __init__(self, rewards, actions):
        self.rewards = rewards
        self.actions = actions
    
    def __str__(self):
        return "Total rewards : %f" % (sum(self.rewards),)

# tirer au hasard un nombre suivant la distribution des gains d'une machine
def action_reward(Q):
    mu, sigma = Q
    return random.gauss(mu, sigma)

# retourne la valeur mise à jour de cur_Q en utilisant reward
# k est le nombre d'elements dont Q est la moyenne
# updated_Q revient à calculer Q = (r1 + r2 + ... rk) / k
# au lieu de le recalculer à chaque fois qu'on reçoit un gain, on le met à jour.
def updated_Q(cur_Q, k, reward):
    return cur_Q + (1./(k + 1)) * (reward - cur_Q)


# Selectionner la meilleure action à chaque fois
def greedy_sel_action(approx_Qs, iteration):
    return approx_Qs.index(max(approx_Qs))

# selectionner l'action avec la méthode epsilon-gloutonne
def epsilon_sel_action(epsilon_getter=lambda iteration:0.9):

    def sel_action(approx_Qs, iteration):
        epsilon = epsilon_getter(iteration)
        v = random.random()
        # avec proba epsilon in choisit l'action qui maximise le retour moyen
        if v <= epsilon:
            return greedy_sel_action(approx_Qs, iteration)
        # avec proba (1 - epsilon), selectionner aléatoirement l'action
        else:
            return random.randint(0, len(approx_Qs) - 1)
    return sel_action

# selectionner l'action avec la méthode softmax
def softmax_sel_action(tau_getter=lambda iteration:1):
    
    def sel_action(approx_Qs, iteration):
        tau = tau_getter(iteration)
        
        # pour normaliser les probabilités
        normalizer = sum(math.exp(Q / tau) for Q in approx_Qs)
        # liste des probabilités de chosir chaque action
        action_probabilities = [math.exp(Q / tau) / normalizer for Q in approx_Qs]
                
        # selectionner l'action aléatoirement en pondérant chaque
        # action avec sa probabilité
        v = random.random()
        accumulated_probabilities = 0
        for action_index, probability in enumerate(action_probabilities):
            accumulated_probabilities += probability
            if v <= accumulated_probabilities:
                return action_index

    return sel_action

def ucb_sel_action(C_getter=lambda _:1):
    global T
    T = [] # Nombre d'occurences de chaque action
    def sel_action(approx_Qs, iteration):
        global T
        if iteration == 0:
            T = [1] * len(approx_Qs) # a l'initialisation T=1 pour toutes les actions
        C = C_getter(iteration)
        # Calcul du score pour chaque action
        ucb_scores = [Q + C * math.sqrt(math.log(iteration + 1) / tb) for Q, tb in zip(approx_Qs, T)]
        # Selectionner le meilleur score
        max_ucb_score = max(ucb_scores)
        best_action = ucb_scores.index(max_ucb_score)
        # Mise a jour du nombre d'occurrence de l'action selectionnee
        T[best_action] += 1
        return best_action

    return sel_action
# generer aleatoirement n couples (moyenne, variance) qui vont décrire la distribution des
# gains des machines. n va être le nombre de machines voulues.
# les distrubtions suivront la loi gaussienne.
def gen_Q(n, min, max, variance):
    return [(random.randint(min, max), variance) for i in xrange(n)]

if __name__ == "__main__":
    # 10 machines, moyennes des gains entre 0 et 100. variances = 1.
    real_Qs = gen_Q(10, 0, 500, 10)
    tries = 1000 # nombre d'essais

    # simuler avec greedy-epsilon avec epsilon=0.9
    r1 = simulate(real_Qs, tries, epsilon_sel_action(lambda _:0.9), updated_Q)
    # simuler avec greedy
    r2 = simulate(real_Qs, tries, greedy_sel_action, updated_Q)
    # simuler avec softmax avec tau=10
    r3 = simulate(real_Qs, tries, softmax_sel_action(lambda _:10), updated_Q)
    # Simuler avec UCB avec C=2000 qui decroit avec le nombre d'iterations
    r4 = simulate(real_Qs, tries, ucb_sel_action(lambda it:2000/(it+1)), updated_Q)
    # afficher les gains cumules
    print "Greedy-epsilon : " + str(r1)
    print "Greedy : " + str(r2)
    print "softmax : " + str(r3)
    print "ucb :" + str(r4)
