import os


def verbose_print(message, verbose=False):
    if verbose or os.getenv("DEBUG_MODE"):
        print(message)
