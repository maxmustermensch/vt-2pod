import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--name')

args = parser.parse_args()


z = np.load(f'TS001/{args.name}')

print(z)