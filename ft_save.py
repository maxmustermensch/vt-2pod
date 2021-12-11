import numpy as np
import pickle
import os

file_name = 'test.p'

new_data = np.zeros(3)
new_data = np.ones(3)

if os.path.isfile(file_name):
	with open(file_name, 'rb') as f:
		old_data = np.array(pickle.load(f))
		new_data = np.append(old_data, new_data, axis = 0)

with open(file_name, 'wb') as f:
	pickle.dump((new_data), f)

with open(file_name, 'rb') as f:
	data = pickle.load(f)

print(data)