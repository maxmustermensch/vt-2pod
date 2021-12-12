import numpy as np
import time
import os

#x = np.array([[[40, 0, "out", "w", 1335], [40, 0, "in", "w", 1336]], [[40, 1, "out", "w", 1337], [40, 1, "in", "w", 1338]], [[40, 2, "out", "y", 1339], [40, 2, "in", "w", 1340]]])

#print("x[0][0][0]", x[0][0][0])
#print("x[0][0][1]", x[0][0][1])
#print("x[0][0][2]", x[0][0][2])
#print("x[0][0][3]", x[0][0][3])
#print("x[0][0][4]", x[0][0][4])

#print(x)
#print(x.shape)
#print("_______________________________________")

TSID = "TS001"
test_mode = "tigh"
timestamp = time.time()

file_name = TSID +"_"+ test_mode +"_"+ str(round(timestamp)) +".npy"
file_path = str(TSID)# + "/"

y = np.empty((0,2,5))

y = np.append(y, [[[40, 3, "out", "w", 1341], [40, 3, "in", "w", 1342]]], axis=0)

y = np.append(y, [[[40, 4, "out", "w", 1343], [40, 4, "in", "w", 1344]]], axis=0)

y = np.append(y, [[[40, 5, "out", "w", 1345], [40, 5, "in", "w", 1346]]], axis=0)

if os.path.isdir(file_path):
    print("directory already existing. overwrite (0), add to it (1) or cancel(2)?")
os.mkdir(file_path)
np.save((file_path + "/" + file_name), y)

z = np.load(file_path +"/"+ file_name)

print(z)


