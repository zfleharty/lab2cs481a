#include <sys/time.h>
#include <unistd.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

void timerhandler(void);

int INTERVAL = 5;
int STOPAT = 2000;
unsigned long timepassed = 0;
int cpuintensive = 0;
int exec_pause_seq = 0;
int debug = 0;

int main(int argc, char *argv[]) {
   struct itimerval it_val;    
   unsigned long i = 0;  
   int opt;
   
   while((opt = getopt(argc,argv,"cs:d:e")) != -1)
     {
       switch(opt)
	 {
	 case 's':
	   INTERVAL = atoi(optarg);
	   STOPAT = 10000 / INTERVAL;
	   break;
	 case 'c':
	   cpuintensive = 1;
	   break;
	 case 'd':
	   STOPAT += atoi(optarg) / INTERVAL;
	   break;
	 case 'e':
	   debug = 1;
	   break;
	 case ':':
	   printf("option needs a value\n");
	   break;
	 case '?':
	   printf("unkown option: %c\n",optopt);
	   exit(2);
	 }
     }
   
   
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
       //if(debug) printf("i: %lu\n",i);
     }
   if(debug)
     {
       printf("\ntotal-process_time: %d\n",(STOPAT * INTERVAL));
       printf("sleeping for %dms\n",(1000 * INTERVAL));
       printf("sleeping for every 10/%d interrupts:\n",INTERVAL);
          
       if(cpuintensive)
	 {
	   printf("i for cpu_process: %lu\n",i);       
	 }else
	 {
	   printf("i for io_process: %lu\n",i);
	 }
     }else
     {
       printf("%lu",i);
     }


}

void timerhandler(void) {
  timepassed++;
  if(!cpuintensive){
    exec_pause_seq++;
    if((exec_pause_seq % (10/INTERVAL)) == 0)
      {
	usleep(1000 * INTERVAL);
      }
  }
}
 
