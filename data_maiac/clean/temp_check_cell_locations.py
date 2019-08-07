import os
import sys
from glob import glob

from pyhdf.SD import SD, SDC

from util.env import src_path
from clean.raw import get_corners


def read_hdf(hdf_path):
    hdf = SD(hdf_path, SDC.READ)
    return hdf


if __name__ == "__main__":
    days = [dns for rt, dns, fns in os.walk(src_path())][0]

    for i in range(len(days) - 1):
        day1 = glob(src_path(days[i], '*.hdf'))
        day2 = glob(src_path(days[i + 1], '*.hdf'))
        for j in range(len(day1)):
            ul1, lr1 = get_corners(read_hdf(day1[j]))
            ul2, lr2 = get_corners(read_hdf(day2[j]))

            try:
                assert (ul1 == ul2)
            except:
                print(f'test {i} failed because {ul1} =/= {ul2}')
                sys.exit()
            try:
                assert (lr1 == lr2)
            except:
                print(f'test {i} failed because {lr1} =/= {lr2}')
                sys.exit()
