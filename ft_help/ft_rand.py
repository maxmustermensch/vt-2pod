import numpy as np

def random_array(bursts_per_position, minmax):
    k = 0

    min_1 = minmax[0]
    max_1 = minmax[1]

    while k==0:
        rand_array = np.rint(np.random.rand(bursts_per_position))
        if sum(rand_array) >= min_1 and sum(rand_array) <= max_1:
            k = 1

    return(rand_array)

count2 = 0
count3 = 0
count4 = 0
count5 = 0
countwrong = 0

for i in range(0,10):
	arr = random_array(7, [2,5])
	summ = sum(arr)
	print (arr)
	if summ == 3:
		count3 = count3 + 1
	elif summ == 2:
		count2 = count2 + 1	
	elif summ == 4:
		count4 = count4 + 1
	elif summ == 5:
		count5 = count5 + 1
	else:
		#countwrong = countwrong +1
		print("THIS IS SO WRONG BABY")

print("2 : ", count2)
print("3 : ", count3)
print("4 : ", count4)
print("5 : ", count5)
#print("? : ", countwrong)