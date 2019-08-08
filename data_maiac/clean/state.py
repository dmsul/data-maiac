import os
from glob import glob

import pandas as pd
import numpy as np
from econtools import load_or_build, state_abbr_to_name

from data_census.clean.cartographic_boundaries.state import state_shape_df

from data_maiac.util.env import src_path, data_path
from data_maiac.clean.raw import aod47_day_df


@load_or_build(data_path('{state_abbr}_{year}_{month}.pkl'))
def aod47_state_month(state_abbr: str, year: int, month: int) -> pd.DataFrame:
    """Aerosol Optical Depth (AOD) (0.47 micrometer) from MODIS Multi-Angle
    Implementation of Atmospheric Correction (MAIAC) as pandas DataFrame.
    Outputs all data for a specified state and month.

    Args:
        state_abbr (str): 2-character US state abbreviation.
        year (int): 4-digit year.
        month (int): Calendar month.

    Returns:
        df (DataFrame): Each row is a MODIS observation in the queried state,
            year, and month.  Columns 'x' and 'y' are longitude and latitude,
            in the sinusoidal transformation, for the gridcell centroid of the
            observation. Column 'aod' is observed AOD in the gridcell. Also
            includes columns 'month', 'year', and 'day'.
    """
    day_list = [
        os.path.split(x)[1] for x in
        glob(src_path(f'{year}.{str(month).zfill(2)}.*'))
    ]
    # Get state's XY bounds
    bounds = _get_state_bounds(state_abbr)

    dfs = [prep_day(date, bounds) for date in day_list]

    return pd.concat(dfs, ignore_index=True)

def _get_state_bounds(state_abbr: str) -> tuple:
    df = state_shape_df(2010, '5m')
    df = df[df['NAME'] == state_abbr_to_name(state_abbr)]
    bounds = df.geometry.bounds.T.squeeze().tolist()
    return tuple(bounds)


def prep_day(date: str, bounds: tuple) -> pd.DataFrame:
    df = aod47_day_df(date)
    minx, miny, maxx, maxy = bounds
    df = df[
        (df['x'] <= maxx) &
        (df['x'] >= minx) &
        (df['y'] <= maxy) &
        (df['y'] >= miny)
    ]
    year, month, day = [int(x) for x in date.split('.')]

    df['year'] = year - 2000
    df['month'] = month
    df['day'] = day

    for col in ('year', 'month', 'day'):
        df[col] = df[col].astype(np.int8)

    return df


if __name__ == "__main__":
    df = aod47_state_month('PA', 2013, 1)
