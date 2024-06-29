import pandas as pd
import numpy as np
import pickle
from io import StringIO
from functools import lru_cache

@lru_cache(maxsize=100, )
def load_pickle(filename):
    with open(filename, 'rb') as file: # read file
        contents = pickle.load(file) # load contents of file
    return contents