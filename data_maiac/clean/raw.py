from glob import glob
from typing import Tuple

import numpy as np
from pyhdf.SD import SD, SDC

from util.env import src_path
from clean.download import hdf_local_filepath


def aod47_flat(hdf: SD) -> np.ndarray:
    # See User Guide page 12
    # https://lpdaac.usgs.gov/documents/110/MCD19_User_Guide_V6.pdf
    aod_dataset = 'Optical_Depth_047'
    fill_value = -28672
    scale_value = 0.001

    aod_table = hdf.select(aod_dataset)
    aod = aod_table[:].astype(np.float32)

    aod[aod == fill_value] = np.nan
    aod = np.nanmean(aod, axis=0)

    aod *= scale_value

    return aod


def get_corners(hdf: SD) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    metadata_str = hdf.attributes()['StructMetadata.0'].replace('\x00', '')
    wtf = metadata_str.replace('\t', '').split('\n')
    points = [x for x in wtf
              if 'UpperLeftPointMtrs' in x or 'LowerRightMtrs' in x]
    assert len(points) == 4

    a, b = points[0].split('=')
    assert a == 'UpperLeftPointMtrs'
    UpperLeftPointMtrs = eval(b)

    a, b = points[1].split('=')
    assert a == 'LowerRightMtrs'
    LowerRightMtrs = eval(b)

    return UpperLeftPointMtrs, LowerRightMtrs


def load_hdf(date: str, filename: str) -> SD:
    hdf_path = hdf_local_filepath(date, filename)
    hdf = SD(hdf_path, SDC.READ)
    return hdf


if __name__ == '__main__':
    date = '2015.01.01'
    filelist = glob(src_path(date, '*.hdf'))
    filename = filelist[0]
    hdf = load_hdf(date, filename)

    aod = aod47_flat(hdf)
    ul, lr = get_corners(hdf)
