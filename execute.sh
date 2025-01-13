#!/bin/bash

END=10
for ((i=10;i<=END;i++)); do
    python3 read-consistancy-checker.py --reuse-session --num-requests $((i * 100)) > ~/log-with-fix-${i}00-request-10iterations-cached-session-and-load-polic-single-place.txt 2>&1
    sleep 60
    echo $i
done
