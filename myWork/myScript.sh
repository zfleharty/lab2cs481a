#!/bin/bash

echo "Mixed"
taskset -c 1 ./usecpuorio -c -e &
taskset -c 1 ./usecpuorio -s 5 -e &
taskset -c 1 ./usecpuorio -s 5 -e &
taskset -c 1 ./usecpuorio -c -e &
taskset -c 1 ./usecpuorio -s 5 -e &
taskset -c 1 ./usecpuorio -s 5 -e &
sleep 240

echo "Just CPU"

taskset -c 1 ./usecpuorio -c -e &
taskset -c 1 ./usecpuorio -c -e &
taskset -c 1 ./usecpuorio -c -e &
taskset -c 1 ./usecpuorio -c -e &
sleep 60
