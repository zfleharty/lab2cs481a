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
    num_cpu_proc_left = tot_CPU_comp - num_cpu_mix # Number of cpu processes to represent with IO processes
    num_io_proc = (int)(num_cpu_proc_left / (1-perc_io)) # number of IO processes
    cpu_time_diff = (10000 * tot_CPU_comp) - (10000 * num_cpu_mix) - ((10000 * (1 - perc_io)) * num_io_proc)
    io_cpu_correction = cpu_time_diff / num_io_proc #time to add or take away from io processes
    io_cpu_correction = 0
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

    return (averages,results,num_io_proc)


def run_scaled_tests(up_to):                                            
   scaled_results = np.array([None] * up_to)                            
                                                                        
   for (i,percentage) in enumerate(np.linspace(.1,(.1*(up_to)),up_to)): 
      scaled_results[i] = scale_processes(4,2,percentage)               
   return scaled_results                                                
                                                                        
def bar_plot(title,cpu_mix,just_cpu_av,io,n_groups,x_lab,x_ticks,y_lab):

   #set up plot
   fig, ax = plt.subplots()
   index = np.arange(n_groups)
   bar_width = 0.20
   opacity = 0.8

   io_rect = plt.bar(index,io,bar_width,alpha=opacity,color='b',label='io_average')
   mix_cpu_rect = plt.bar(index+bar_width,cpu_mix,bar_width,alpha=opacity,color='r',label='mix_cpu_average')
   just_cpu_rect = plt.bar(index+(2*bar_width),just_cpu_av,bar_width,alpha=opacity,color='g',label='just_cpu_av')

   plt.title(title)
   plt.xlabel(x_lab)
   plt.ylabel(y_lab)
   plt.xticks(index + bar_width, x_ticks)
   plt.legend()
   plt.tight_layout()
   plt.savefig(title + ".pdf")

def run_tests():
   num_tests = 9                                                           
   results = run_scaled_tests(num_tests)                                   
   full_cpu_av = np.array([av[2] for (av,r,i) in results])                 
   mix_cpu_av = np.array([av[0] for (av,r,i) in results])              
   io_av = np.array([av[1] for (av,r,i) in results])
   num_io = np.array([i for (av,r,i) in results])      
   x_ticks = np.array([str(x) + "(" +str(io)+")" for x,io in zip(np.arange(10,100,10),num_io)])
   x_lab = "percentage io and (number of I/O processes used)"
   y_lab = "average cpu time (value of i)"
   title = "CPU average time for processes"
   bar_plot(title,mix_cpu_av,full_cpu_av,io_av,num_tests,x_lab,x_ticks,y_lab)                                                                        



# plt.figure()                                                            
# plt.set_title("CPU Processes Average Time")                             
# plt.ylabel("average cpu time");                                         
# plt.xlabel("IO percentage run concurrently with CPU")                   
# plt.plot(xs,ys)                                                         
# plt.savefig("cpu_averages.pdf")                                         


