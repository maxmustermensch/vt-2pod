import numpy as np
import time
import os
import datetime

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
timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M')

file_name = TSID +"_"+ test_mode +"_"+ timestamp +".npy"
file_path = str(TSID)# + "/"

y = np.empty((0,2,5))

y = np.append(y, [[[40, 3, "out", "w", round(time.time(), 3)], [40, 3, "in", "w", round(time.time(), 3)]]], axis=0)
y = np.append(y, [[[40, 4, "out", "w", round(time.time(), 3)], [40, 4, "in", "w", round(time.time(), 3)]]], axis=0)
time.sleep(1)
y = np.append(y, [[[40, 5, "out", "w", round(time.time(), 3)], [40, 5, "in", "w", round(time.time(), 3)]]], axis=0)


def save_mgmt(data_arr):
    '''
    IN:
    OUT:
    DO:
    '''

    #check for directory with TSID
    if not os.path.isdir(file_path):
        os.mkdir(file_path)
        print("new directory " + TSID + " created")

    np.save(os.path.join(file_path, file_name), data_arr)
    return

save_mgmt(y)

time.sleep(1)

z = np.load(os.path.join(file_path, file_name))

print(z)

