#!/bin/bash

echo "Mixed"
taskset -c 0 ./usecpuorio -c -e &
taskset -c 0 ./usecpuorio -s 5 -e &
taskset -c 0 ./usecpuorio -s 5 -e &
taskset -c 0 ./usecpuorio -c -e &
taskset -c 0 ./usecpuorio -s 5 -e &
taskset -c 0 ./usecpuorio -s 5 -e &
sleep 60

echo "Just CPU"

taskset -c 0 ./usecpuorio -c -e &
taskset -c 0 ./usecpuorio -c -e &
taskset -c 0 ./usecpuorio -c -e &
taskset -c 0 ./usecpuorio -c -e &
sleep 60
