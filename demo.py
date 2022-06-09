import numpy as np
import  pandas as pd

similarity_matrix = pd.DataFrame(np.zeros((19834, 19834)), index=range(19834), columns=range(19834))
print(similarity_matrix)