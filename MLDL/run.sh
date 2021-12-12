#/bin/bash

#for dataset in btc_trend btc_wiki btc_trend_wiki 
for dataset in btc_wiki btc
do
	for sf in -1 0 1
	do
		echo $dataset $sf
		python main.py -d $dataset -s $sf
	done
done
