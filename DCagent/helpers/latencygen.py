import sys
import random
import time

num_clients = int(sys.argv[1])

print('[LATENCY]')

for i in range(1,num_clients + 1):
    print('CL' + str(i) + ' = ' + str(pow(random.random(), 4) * 1000))


