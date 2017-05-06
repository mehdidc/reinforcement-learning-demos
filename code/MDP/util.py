import random

def select_using_probability(elements, probabilities):
    n = random.random()
    cumulated_probabilities = 0
    for element, probability in zip(elements, probabilities):
        cumulated_probabilities += probability
        if n <= cumulated_probabilities:
            return element
    
    raise Exception("probas do not sum up to one")

def modulo(L, m):
    return (v for i, v in enumerate(L) if (i % m) == 0)

def cache(f):
    values = {}

    def F(*args):
        if args in values:
            return values[args]
        else:
            value = f(*args)
            values[args] = value
            return value
    return F
