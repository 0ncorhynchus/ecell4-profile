#!/bin/bash

methods=(vol conc)
factories=(spatiocyte egfrd egfrd.bd bd.bd meso)

seed=$1
if [ -z "$seed" ]; then
    seed=0
fi

for m in ${methods[@]}; do
    for f in ${factories[@]}; do
        nohup python profile.py $m $f $seed > log/${m}_${f}.out &
    done
done

