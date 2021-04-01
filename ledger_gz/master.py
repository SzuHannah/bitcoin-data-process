import os
import time
from multiprocessing import Pool
from datetime import timedelta


processes = ('process1.py','process2.py','process3.py')

def run_process(process):
	os.system('python {}'.format(process))

start_time = time.time()
pool = Pool(processes=3)
pool.map(run_process,processes)

end_time = time.time()
print(timedelta(seconds=end_time-start_time))
