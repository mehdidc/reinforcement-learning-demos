# -*- coding: utf-8 -*- 

import matplotlib.pyplot as plt
from bandit import *

# genere des moyennes pour 'nb_tests' tests. leur moyenne va etre selectionnee
# aleatoirement dans l'intervalle [min_mean,max_mean]
def generate_tests(nb_tests, nb_actions=10, min_mean=0, max_mean=100, variance=1):
    tests = []
    for i in xrange(nb_tests):
        real_Qs = gen_Q(nb_actions, min_mean, max_mean, variance)
        tests.append(real_Qs)
    return tests

# Simuler plusieurs methodes sur plusieurs tests
# - sel_action_methods est une liste de methodes a appliquer
# - tests est un ensemble de tests generes avec 'generate_tests'
# - tries fixe le nombre d'iterations pour chaque test
# Cette fonction retournera les resultats sous forme de liste
# ou chaque element de la liste represente les resultats d'une methode.
# les resultats d'une methode est une liste d'objets 'Result'.
# chaque element de cette liste constitue le resultat d'une methode pour un test.
def simulate_on_tests(tests, sel_action_methods, tries=100):
    results = []
    for sel_action_method in sel_action_methods:
        method_results = []
        for test_real_Qs in tests:
            method_result = simulate(test_real_Qs, tries, sel_action_method, updated_Q)
            method_results.append(method_result)
        results.append(method_results)
    return results

def cumulated_rewards(rewards):
    cumulated = 0
    for reward in rewards:
        cumulated += reward
        yield cumulated

# utilisee avec plot_method_results pour afficher l'evolution des rewards
# en fonction de l'iteration.
# pour chaque methode, a chaque iteration, le reward est la moyenne
# des rewards obtenus dans tous les tests pour cette iteration.
def method_rewards_average(tests_results, tests):
    rewards = list((result.rewards) for result in tests_results)
    for iteration_rewards in zip(*rewards):
       average = mean(iteration_rewards)
       yield average

# utilisee avec plot_method_results pour afficher l'evolution des pourcentages
# de selection de la meilleure action en fonction de l'iteration.
# pour chaque methode, a chaque iteration, le pourcentage est le nombre
# de tests dans lequel la meilleure action a ete choisie
def method_percentage_sel_best_action(tests_results, tests):
    actions = list((result.actions for result in tests_results))
    for iteration_actions in zip(*actions):
        nb_good_actions = 0
        for test, action in zip(tests, iteration_actions):
            best_action = max(test)
            best_action_index = test.index(best_action)
            if action == best_action_index:
                nb_good_actions += 1 
        nb_good_actions = 100. * float(nb_good_actions) / len(tests)
        yield nb_good_actions

def mean(L):
    return sum(L) / len(L)


COLORS = [
    'red', 'blue', 'grey', 'yellow', 'green'
]

# Dessine une courbe montrant l'evolution d'une quantitée calculée à partir des resultats
# des simulations. cette quantitiée est calculée à l'aide de aggregate_func.
# tests : les tests sur lesquels les simulations ont été faites
# methods_names : le label qui sera associé aux methodes dans le graphe
# methods_tests_results : les résultats des tests
def plot_methods_results(tests, methods_names, methods_tests_results, aggregate_func, xlabel='Iteration', ylabel='',colors=None):
    if colors is None:
        colors = COLORS

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    data = []
    for method, tests_results, color in zip(methods_names, methods_tests_results, colors):
        aggregation = aggregate_func(tests_results, tests)
        data = list(aggregation)
        plt.plot(xrange(1, len(data)+1), data, color=color, label=method)
    plt.legend(loc='best')
    plt.show()

if __name__ == "__main__":
    tests = generate_tests(500, variance=10)
    
    epsilon1, epsilon2, tau, C = 0.9, 0.2, 20, 1000
    methods_names = [
            "Greedy epsilon ($\epsilon=%.2f$)" % (epsilon1,),
            "Greedy epsilon ($\epsilon=%.2f$)" % (epsilon2,),
            "Greedy",
            "Softmax ($\\tau=%.2f$)" % (tau,),
            "UCB ($C = %.2f$)" % (C,),
    ]
    methods = [
            epsilon_sel_action(lambda it:epsilon1),
            epsilon_sel_action(lambda it:epsilon2),
            greedy_sel_action,
            softmax_sel_action(lambda it:tau),
            ucb_sel_action(lambda it:float(C)/(it+1)),
    ]
    results = simulate_on_tests(tests, methods)
    plot_methods_results(tests, methods_names, results, method_rewards_average, ylabel='Average reward')
    plot_methods_results(tests, methods_names, results, method_percentage_sel_best_action, ylabel='Percentage of selecting the best action')
