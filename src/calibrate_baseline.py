from __future__ import annotations
import argparse
import pandas as pd
from .baseline_manager import BaselineManager


def main():
    p=argparse.ArgumentParser(); p.add_argument("csv"); p.add_argument("--node", default="NODE_A")
    args=p.parse_args(); df=pd.read_csv(args.csv); mgr=BaselineManager(args.node)
    records=df.to_dict("records"); print(mgr.calibrate(records))

if __name__ == "__main__": main()
