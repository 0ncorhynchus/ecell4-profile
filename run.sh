#!/bin/bash

methods=(vol conc)
factories=(spatiocyte egfrd egfrd.bd bd.bd meso)

seed=$1

for m in ${methods[@]}; do
  for f in ${factories[@]}; do
    fname=${f}_fixed_${m}
    echo "seed=$seed" >> log/${fname}.out
    nohup python profile.py $m $f $seed > tsv/${fname}.tsv 2>> log/${fname}.out &
  done
done

