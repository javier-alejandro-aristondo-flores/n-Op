#!/bin/bash
# runs the branch-trunk re-scoring once the first queue has finished
cd /home/javier/Projects/Physics/Programs/n-Op-streams/audit-fixes/audits/2026-09-25
while pgrep -f "scripts/a7_queue.sh" > /dev/null; do sleep 30; done
echo "$(date +%H:%M:%S) starting branch_trunk" >> outputs/a7-queue.log
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 taskset -c 12-15 nice -n 10 \
    /home/javier/Projects/Physics/Programs/n-Op/.venv/bin/python scripts/a7_branch_trunk.py outputs/a7-branch_trunk.json > outputs/a7-branch_trunk.log 2>&1; /home/javier/Projects/Physics/Programs/n-Op/.venv/bin/python scripts/a7_fixed_basis.py outputs/a7-fixed_basis.json > outputs/a7-fixed_basis.log 2>&1
echo "$(date +%H:%M:%S) finished branch_trunk with exit $?" >> outputs/a7-queue.log
