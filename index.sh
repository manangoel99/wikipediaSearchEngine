#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate IRE
python indexer.py $1 $2 $3