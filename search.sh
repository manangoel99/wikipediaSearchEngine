#!/bin/bash
eval "$(conda shell.bash hook)"
conda activate IRE
python search.py $1 $2