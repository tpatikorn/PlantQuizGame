import os


# print if explicitly verbose, or DEBUG_MODE = True
# set DEBUG_MODE in .env
def verbose_print(message, verbose=False):
    if verbose or os.getenv("DEBUG_MODE"):
        print(message)
