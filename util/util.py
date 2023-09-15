import random


# print if explicitly verbose
def verbose_print(message, verbose=False):
    if verbose:
        print(message)


def set_seed(seed=None):
    if seed is None:
        seed = random.random()
    random.seed(seed)
    return seed
