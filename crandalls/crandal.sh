#!/bin/bash

echo "Mixed"
taskset -c 0 ./usecpuorio CPU &
taskset -c 0 ./usecpuorio &
taskset -c 0 ./usecpuorio &
taskset -c 0 ./usecpuorio CPU &
taskset -c 0 ./usecpuorio &
taskset -c 0 ./usecpuorio &
sleep 60

echo "Just CPU"

taskset -c 0 ./usecpuorio CPU &
taskset -c 0 ./usecpuorio CPU &
taskset -c 0 ./usecpuorio CPU &
taskset -c 0 ./usecpuorio CPU &
sleep 60
