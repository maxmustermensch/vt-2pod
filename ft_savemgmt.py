import numpy as np
import time
import os
import shutil
import sys
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
timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d_%H:%M:%S')

file_name = TSID +"_"+ test_mode +"_"+ timestamp +".npy"
file_path = str(TSID)# + "/"

y = np.empty((0,2,5))

y = np.append(y, [[[40, 3, "out", "w", 1341], [40, 3, "in", "w", 1342]]], axis=0)
y = np.append(y, [[[40, 4, "out", "w", 1343], [40, 4, "in", "w", 1344]]], axis=0)
y = np.append(y, [[[40, 5, "out", "w", 1345], [40, 5, "in", "w", 1346]]], axis=0)


def save_mgmt(dir_check, data_arr):
    '''
    IN:
    OUT:
    DO:
    '''
    if dir_check:
        #check for directory with TSID and ask USR how to deal with it
        if os.path.isdir(file_path):
            while True:
                USR_select = input("directory already existing. overwrite (0) or cancel(1): ")
                if USR_select == "0":
                    shutil.rmtree(file_path)
                    os.mkdir(file_path)
                    return
                elif USR_select == "1":
                    sys.exit()
                else:
                    print("unacceptable input\n")
        else:
            os.mkdir(file_path)
            print("new directory " + TSID + " created")
        return
    else:
        np.save((file_path + "/" + file_name), data_arr)
        return

save_mgmt(True, None)

save_mgmt(False, y)

time.sleep(1)

z = np.load(file_path +"/"+ file_name)

print(z)

test = time.time()
print(test/60/60/24/365.24)


