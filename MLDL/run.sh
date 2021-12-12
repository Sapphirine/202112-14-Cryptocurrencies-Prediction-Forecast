#/bin/bash

for dataset in btc btc_trend btc_wiki btc_trend_wiki 
do
	for sf in -1 0 1
	do
		for nfils in 32 
		do
			for mdil in 3 4 5
			do
				echo $dataset $sf $nfils $mdil
				python main.py -d $dataset -s $sf --n_filters $nfils --max_dilation $mdil 
			done
		done
	done
done
