#/bin/bash

for dataset in btc btc_trend
do
	for smooth in 0 1 
	do
		for window in 30 60 
		do
			for sf in -1 0 1
			do
				for nfils in 32 64 
				do
					for mdil in 3 4 5 6 7
					do
						for batch_size in 16 32 
						do
							python main.py -d $dataset -s $sf --n_filters $nfils --max_dilation $mdil 
						done
					done
				done
			done
		done
	done
done
