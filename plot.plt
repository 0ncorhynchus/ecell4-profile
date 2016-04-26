set terminal postscript eps enhanced color
set output 'benchmark.eps'
set logscale x
set logscale y
set xlabel 'N [#particles]'
set ylabel 'real time / simulation time'
plot 'tsv/spatiocyte_fixed_vol.tsv'  u 1:2:3 w yerrorbars t 'spatiocyte vol', \
     'tsv/spatiocyte_fixed_conc.tsv' u 1:2:3 w yerrorbars t 'spatiocyte conc', \
     'tsv/egfrd_fixed_vol.tsv'       u 1:2:3 w yerrorbars t 'egfrd vol', \
     'tsv/egfrd_fixed_conc.tsv'      u 1:2:3 w yerrorbars t 'egfrd conc', \
     'tsv/meso_fixed_vol.tsv'        u 1:2:3 w yerrorbars t 'meso vol', \
     'tsv/meso_fixed_conc.tsv'       u 1:2:3 w yerrorbars t 'meso conc', \
     'tsv/bd.bd_fixed_vol.tsv'       u 1:2:3 w yerrorbars t 'bd.bd', \
     'tsv/egfrd.bd_fixed_conc.tsv'   u 1:2:3 w yerrorbars t 'egfrd.bd'
