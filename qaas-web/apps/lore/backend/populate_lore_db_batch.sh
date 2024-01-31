#!/bin/bash

start=0

size=100000

runs=6

# Loop to run the script multiple times
for ((i=1; i<=runs; i++))
do
  echo "Running script with --start $start --size $size"
  python3 populate_lore_db_in_batch.py --start $start --size $size

  # Increment start for next run
  start=$((start + size))
done
