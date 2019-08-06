from glob import glob
import sys

from pyhdf.SD import SD, SDC

from util.env import src_path
from clean.raw import get_corners


def read_hdf(hdf_path):
    hdf = SD(hdf_path, SDC.READ)
    return hdf


if __name__ == "__main__":
    day1 = glob(src_path('2000.06.05', '*.hdf'))
    day2 = glob(src_path('2015.04.11', '*.hdf'))

    for i in range(len(day1)):
        ul1, lr1 = get_corners(read_hdf(day1[i]))
        ul2, lr2 = get_corners(read_hdf(day2[i]))

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
