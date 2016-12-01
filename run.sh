#!/bin/bash

MUTEX=$(ps aux|grep -q "python huna_crawler.p[y]")
if [[ $? -eq 1 ]]; then
	python huna_crawler.py &
else
	echo "Already Running"
fi
