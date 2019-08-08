from glob import glob
from typing import Tuple

import numpy as np
import pandas as pd
from pyhdf.SD import SD, SDC
from econtools import load_or_build

from data_maiac.util.env import data_path
from data_maiac.util.gis import sinu
from data_maiac.clean.download import hdf_local_filepath

SCALE_VALUE_47 = 0.001


@load_or_build(data_path('aod47_{date}.pkl'))
def aod47_day_df(date: str) -> pd.DataFrame:
    """Aerosol Optical Depth (AOD) (0.47 micrometer) from MODIS Multi-Angle
    Implementation of Atmospheric Correction (MAIAC) as pandas DataFrame.
    Outputs all data for a specified date. Extent is full US.

    Args:
        date (str): Date in the format 'YYYY.MM.DD'.

    Returns:
        df (DataFrame): Each row is a MODIS observation from the given date.
            Columns 'x' and 'y' are longitude and latitude, in the sinusoidal
            transformation, for the gridcell centroid of the observation.
            Column 'aod' is observed AOD in the gridcell.
    """
    filelist = glob(hdf_local_filepath(date, '*.hdf'))
    if len(filelist) == 0:
        raise ValueError(f"No HDF files found for {date}")
    dfs = [aod47_day_grid_df(f) for f in filelist]
    df = pd.concat(dfs, ignore_index=True)

    # De-scale to make it easier to store as int16
    df['aod'] /= SCALE_VALUE_47
    df['aod'] = df['aod'].astype(np.int16)

    # Convert sinusoidal to lat/lon
    df['x'], df['y'] = sinu(df['x'].values, df['y'].values, inverse=True)
    for col in ('x', 'y'):
        df[col] = df[col].astype(np.float32)

    df.columns.name = date

    return df


def aod47_day_grid_df(filepath: str) -> pd.DataFrame:
    hdf = load_hdf(filepath)

    aod = aod47_flat(hdf)
    ul, lr = get_corners(hdf)
    x, y = get_xy(aod, ul, lr)

    df = aod47_combine_todf(aod, x, y)

    return df


def load_hdf(filepath: str) -> SD:
    hdf = SD(filepath, SDC.READ)
    return hdf


def aod47_flat(hdf: SD) -> np.ndarray:
    # See User Guide page 12
    # https://lpdaac.usgs.gov/documents/110/MCD19_User_Guide_V6.pdf
    aod_dataset = 'Optical_Depth_047'
    fill_value = -28672
    SCALE_VALUE_47 = 0.001

    aod_table = hdf.select(aod_dataset)
    aod = aod_table[:].astype(np.float32)

    aod[aod == fill_value] = np.nan
    aod = np.nanmean(aod, axis=0)

    aod *= SCALE_VALUE_47

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


def get_xy(aod: np.ndarray,
           ul: Tuple[float, float],
           lr: Tuple[float, float]) -> Tuple[np.ndarray, np.ndarray]:
    N = aod.shape[0]    # Should be 1200
    diff = abs(ul[0] - lr[0]) / N
    diff_half = diff / 2

    xs = [ul[0] + diff_half + (diff * i) for i in range(N)]
    ys = [ul[1] - diff_half - (diff * j) for j in range(N)]

    master_x, master_y = np.meshgrid(xs, ys)

    return master_x, master_y


def aod47_combine_todf(aod: np.ndarray,
                       x: np.ndarray,
                       y: np.ndarray) -> pd.DataFrame:
    aod_nonmiss = ~np.isnan(aod)
    aod2 = aod[aod_nonmiss].flatten()
    x2 = x[aod_nonmiss].flatten()
    y2 = y[aod_nonmiss].flatten()

    df = pd.DataFrame(
        np.hstack(
            (aod2.reshape(-1, 1),
             x2.reshape(-1, 1),
             y2.reshape(-1, 1)
             )
        ), columns=['aod', 'x', 'y']
    )

    return df


if __name__ == "__main__":
    df = aod47_day_df(f'2015.01.10')
