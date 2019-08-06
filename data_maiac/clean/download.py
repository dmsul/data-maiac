import os
import sys
from typing import List, Optional, Dict

from bs4 import BeautifulSoup
import requests

from util.env import src_path

US_HV_BOUNDS: Dict[int, tuple] = {
    # Keys is V; tuples are matching H
    4: (8, 9, 10, 11, 12, 13),
    5: (8, 9, 10, 11, 12),
    6: (8, 9, 10),
}

ROOT_URL = 'https://e4ftl01.cr.usgs.gov/MOTA/MCD19A2.006'

# Loop over all dates...
# Download all HDF files that are in H and V ranges and aren't already on disk


def main(year: int) -> None:
    session = None
    this_year = [x for x in get_all_dates() if int(x[:4]) == year]
    for date in this_year[5:35]:
        for filename in files_on_date(date):
            if not hdf_file_is_in_US(filename):
                continue
            elif os.path.exists(hdf_local_filepath(date, filename)):
                continue
            elif not session:
                session = download_file(date, filename)
            else:
                download_file(date, filename, session)


def hdf_local_filepath(date: str, filename: str) -> str:
    return src_path(date, filename)


def hdf_file_is_in_US(filename: str) -> bool:
    hv_section = filename.split('.')[2]
    h, v = [int(x) for x in hv_section.replace('h', '').split('v')]
    if v in US_HV_BOUNDS:
        return h in US_HV_BOUNDS[v]
    else:
        return False


def get_all_dates() -> List[str]:
    """ Return a list of all dates on the main MAIAC data page """
    html_doc = requests.get(ROOT_URL).text
    soup = BeautifulSoup(html_doc, 'html.parser')

    all_links = [link.get('href') for link in soup.find_all('a')]
    all_dates = [x for x in all_links if x[:2] == '20']

    return all_dates


def files_on_date(date: str) -> List[str]:
    """ Returns a list of all HDF files for the given date """
    html_doc = requests.get(ROOT_URL + f'/{date}').text
    soup = BeautifulSoup(html_doc, 'html.parser')

    all_links = [link.get('href') for link in soup.find_all('a')]
    all_hdf_files = [x for x in all_links if x[-3:] == 'hdf']

    return all_hdf_files


def download_file(date: str, filename: str, session:
                  Optional[requests.Session]=None) -> requests.Session:
    """ Create src/date/ directory if it doesn't exist.
        Download and save hdf file. """

    date_dir = src_path(date)
    if not os.path.exists(date_dir):
        print(f'Creating directory: {date_dir}')
        os.mkdir(date_dir)

    if session is None:
        session, username, password = initiate_earthdata_session()
        req = session.request('get', hdf_file_url(date, filename))
        r = session.get(req.url, auth=(username, password))
    else:
        req = session.request('get', hdf_file_url(date, filename))
        r = session.get(req.url)

    if r.ok:
        print(f"Downloading {filename}...", end='', flush=True)
        with open(hdf_local_filepath(date, filename), 'wb') as f:
            f.write(r.content)
        print("Done!", flush=True)
    else:
        print("FAILURE!!")
        sys.exit(1)

    return session


def initiate_earthdata_session():
    session = requests.Session()
    username = input("Username: ")
    password = input("Password: ")

    return session, username, password


def hdf_file_url(date: str, filename: str) -> str:
    return ROOT_URL + '/' + date + '/' + filename


if __name__ == "__main__":
    # all_dates = get_all_dates()
    # a_date = all_dates[1000]
    # example_list_of_hdf_files = files_on_date(a_date)
    # # Test downloading a file below
    # session = download_file(a_date, example_list_of_hdf_files[6])
    # download_file(a_date, example_list_of_hdf_files[7], session)
    main(2015)
