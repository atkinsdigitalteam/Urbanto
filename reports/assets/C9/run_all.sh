#!/bin/sh
# Runs the C9 Python benchmark series. One metric per process so peak RSS is per metric.
# Usage: sh run_all.sh > results_python.jsonl
B="python3 $(dirname "$0")/bench_walk.py"
for P in 10000 25000 50000 100000; do
  for M in a1 a1nx a2 a2nx d; do $B --plots $P --graph fine --metric $M; done
  $B --plots $P --graph fine --metric c --k 100
  $B --plots $P --graph fine --metric b --workers 4
done
$B --plots 10000  --graph fine --metric b --workers 1
$B --plots 100000 --graph fine --metric b --workers 1
for M in a1 a2 d; do $B --plots 200000 --graph fine --metric $M; done
$B --plots 200000 --graph fine --metric b --workers 4
for M in a1 a2 b d; do $B --plots 100000 --graph coarse --metric $M; done
$B --plots 100000 --graph coarse --metric c --k 100
