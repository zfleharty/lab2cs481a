import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import subprocess as sp
from threading import Thread

#verify and save 
IOCPU_process_path = "./usecpuorio"
debug = False
if(len(sys.argv) > 1):
   if(sys.argv[1] == "debug"):
       debug = True
        
###############functions for executing processes concurrently#############
#just_cpu: whether or not to run a CPU intensive process or include IO
#cpu: percentage of IO (.1 corresponds to 10 percent)
#cpu_change: If cpu total time needs to be changed for each io process
#results: array to retunr results in
#i: where to put results in array corresponding to the thread
def execute_process(just_cpu,cpu,cpu_change,results,i):
    if(just_cpu):
        result = sp.check_output(["taskset","-c","0",IOCPU_process_path,"-c"])
    else:
        cpu = int(cpu * 10)
        if(debug):
            print("################execute_process of io_call##############")
            print("cpu: " + str(cpu))
            print("cpu_change: " + str(cpu_change))
            print("###############END############\n\n")
        result = sp.check_output(["taskset","-c","0",IOCPU_process_path,"-s",str(cpu),"-d",str(cpu_change)])
    results[i] = long(result)

#num_procs: number of processes to start and reaturn
#cpu: percentage of IO for cpu (.1 corresponds to 10 percent) 1 means to run CPU only processes
#results: array to return results into length must match num_procs
#cpu_change: If cpu total time needs to be changed for each io process
def launch_processes(num_procs,cpu,results,cpu_change=0):
    if(cpu==1):
        just_cpu=True
    else:
        just_cpu=False

    if(debug):
        print("############launch_processes###############")
        print("is cpuIntensive? "+ str(just_cpu))
        print("number of processes given: " + str(num_procs))
        print("cpu given: " + str(cpu))
        print("cpu_change: " + str(cpu_change))
        print("##############END##############\n\n")

    threads = np.array([None] * num_procs)
    for i in np.arange(num_procs):
        threads[i] = Thread(target=execute_process, args=(just_cpu,cpu,cpu_change,results,i))
        threads[i].start()
    return threads

#tot_CPU_comp: Number of just_cpu processes comparing against
#num_cpu_mix: number of CPU processes to run in multi-threaded test
#perc_io: percentage of io for processes to use
def scale_processes(tot_CPU_comp,num_cpu_mix,perc_io):
    ######Calculate scaled environment###############
    num_cpu_proc_left = tot_CPU_comp - num_cpu_mix; # Number of cpu processes to represent with IO processes
    num_io_proc = (int)(num_cpu_proc_left / perc_io); # number of IO processes
    cpu_time_diff = (10000 * tot_CPU_comp) - (10000 * num_cpu_mix) - ((10000 * (1 - perc_io)) * num_io_proc)
    io_cpu_correction = cpu_time_diff / num_io_proc #time to add or take away from io processes

    if(debug):
        print("#########scale Calculated###############")
        print("cpu_processes: " + str(num_cpu_mix))
        print("num_io_proc: " + str(num_io_proc))
        print("io_cpu_correction: " + str(io_cpu_correction))
        print("IO_percentage: " + str(perc_io))
        print("###########END#############\n\n")

    def wait(threads):
        for thread in threads:
            thread.join()
    
    #########launch scaled proccesses#############

    io_result = np.zeros(num_io_proc)
    mix_cpu_result = np.zeros(num_cpu_mix)
    just_cpu_result = np.zeros(tot_CPU_comp)


    mix_cpu_threads = launch_processes(num_cpu_mix,1,mix_cpu_result)
    io_threads = launch_processes(num_io_proc,perc_io,io_result,cpu_change=io_cpu_correction)
    wait(np.concatenate((mix_cpu_threads,io_threads)))

    just_cpu_threads = launch_processes(tot_CPU_comp,1,just_cpu_result)
    wait(just_cpu_threads)

    mix_cpu_average = np.sum(mix_cpu_result) / num_cpu_mix
    io_average = np.sum(io_result) / num_io_proc
    just_cpu_average = np.sum(just_cpu_result) / tot_CPU_comp

    averages = np.array([mix_cpu_average,io_average,just_cpu_average])
    results = np.concatenate((mix_cpu_result,io_result,just_cpu_result))

    return (averages,results)


##########run multiple scaled tests####################
ten_percent_io = scale_processes(4,2,.1)
twenty_percent_io = scale_processes(4,2,.2)
thirty_percent_io = scale_processes(4,2,.3)
fourty_percent_io = scale_processes(4,2,.4)
fifty_percent_io = scale_processes(4,2,.5)
sixty_percent_io = scale_processes(4,2,.6)
seventy_percent_io = scale_processes(4,2,.7)
eighty_percent_io = scale_processes(4,2,.8)
ninety_percent_io = scale_processes(4,2,.9)
