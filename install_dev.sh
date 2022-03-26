#!/bin/bash

conda remove -n qp --all
conda create -n qp python=3.7 scipy
source activate qp
pip install -r requirements_dev.txt

