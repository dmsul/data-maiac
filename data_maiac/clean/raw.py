from clean.download import hdf_local_filepath
from pyhdf.SD import SD, SDC


def load_hdf(date, filename):
    hdf_path = hdf_local_filepath(date, filename)
    hdf = SD(hdf_path, SDC.READ)
    return hdf


if __name__ == '__main__':
    date = '2015.01.01'
    filename = 'MCD19A2.A2015001.h08v05.006.2018101212324.hdf'
    hdf = load_hdf(date, filename)
    print(hdf)
