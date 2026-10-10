#!/bin/bash
# runs the remaining re-scoring jobs one at a time after the ladder rungs finish, logging each to outputs/
cd /home/javier/Projects/Physics/Programs/n-Op-streams/audit-fixes/audits/2026-09-25
while pgrep -f "scripts/a7_flagship_ladder.py outputs" > /dev/null; do sleep 20; done
for job in two_input galerkin correction manifold branch_trunk; do
    echo "$(date +%H:%M:%S) starting $job" >> outputs/a7-queue.log
    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 taskset -c 12-15 nice -n 10 \
        /home/javier/Projects/Physics/Programs/n-Op/.venv/bin/python scripts/a7_$job.py outputs/a7-$job.json > outputs/a7-$job.log 2>&1
    echo "$(date +%H:%M:%S) finished $job with exit $?" >> outputs/a7-queue.log
done
