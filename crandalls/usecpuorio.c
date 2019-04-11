#include <sys/time.h>
#include <unistd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#define INTERVAL 5
#define STOPAT 2000

void timerhandler(void);

unsigned long timepassed = 0;
int cpuintensive = 0;
int exec_pause_seq = 0;
int debug = 0;

int main(int argc, char *argv[]) {
   struct itimerval it_val;    
   if(argc > 1) cpuintensive = 1;
   unsigned long i = 0; 
   
   if (signal(SIGALRM, (void (*)(int)) timerhandler) == SIG_ERR) {
       perror("Unable to catch SIGALRM");
       exit(1);
   }
   
   it_val.it_value.tv_sec = INTERVAL/1000;
   it_val.it_value.tv_usec = (INTERVAL*1000) % 1000000;
   it_val.it_interval = it_val.it_value;
   if (setitimer(ITIMER_REAL, &it_val, NULL) == -1) {
       perror("error calling setitimer()");
       exit(1);
   }

   while (!(timepassed > STOPAT))
     {
       i++;
       if(debug) printf("i: %lu\n",i);
     }
   
   if (cpuintensive){
       printf("i for CPU is %lu\n", i);
   }else{
       printf("i for I/O is %lu\n", i);
   }
}

void timerhandler(void) {
  timepassed++;
  if(debug) printf("timepassed: %lu\n",timepassed);
  
  if(!cpuintensive){
    exec_pause_seq++;
    if((exec_pause_seq % 2) == 0)
      {
	usleep(5000);
	if(debug)printf("slept for 5 ms\n");
      }
  }
}
