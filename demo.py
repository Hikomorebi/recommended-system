import numpy as np
import  pandas as pd
import math

a = [0.2310043668122205, 0.1310043668122205]
b = [-76.0, 14.0]
print(np.corrcoef(np.array(a), np.array(b))[0][1])