import numpy as np
import scipy.stats as st

def random_array(arr_len):
    '''
    IN:
    OUT:
    DO:
    - erstellt 
    '''
    k = 0

    conf_int = st.norm.interval(alpha=.99, loc=arr_len/2, scale = 1)

    min_1 = int(round(conf_int[0]))
    max_1 = int(round(conf_int[1]))

    #print(f'{min_1}, {max_1}')

    while k==0:
        rand_array = np.rint(np.random.rand(arr_len))
        if sum(rand_array) >= min_1 and sum(rand_array) <= max_1:
            k = 1

    return(rand_array)


#print(sum(random_array(50)))

x = 0

for i in range(0,10000):
	x = x + sum(random_array(50))

print(x/10000)