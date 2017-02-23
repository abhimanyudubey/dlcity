import pydistmesh
import numpy as np
import os,sys
import argparse

parser = argparse.ArgumentParser('Generate uniform mesh of points from CSV file')

parser.add_argument('-i', '--input', help='input folder with CSV files', type=str, required=True)
parser.add_argument('-o', '--output', help='output folder to generate points in', type=str, required=True)
parser.add_argument('-s', '--scale', help='scale factor for point generation', type=float, required=True)
