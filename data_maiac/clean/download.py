from typing import List
from bs4 import BeautifulSoup
import requests
from util.env import src_path

US_H_MIN = 7
US_H_MAX = 13
US_V_MIN = 2
US_V_MAX = 6

ROOT_URL = 'https://e4ftl01.cr.usgs.gov/MOTA/MCD19A2.006'

# Loop over all dates...
# Download all HDF files that are in H and V ranges and aren't already on disk


def main() -> None:
    # TODO: INCOMPLETE FUNCTION
    all_dates = get_all_dates()
    for date in all_dates:
        files_for_date = files_on_date(date)
        for filename in files_for_date:
            if not hdf_file_is_in_US(filename):
                continue
            # elif already on disk, `continue`
            # Else, call `download_file`
            pass


def hdf_local_filepath(date: str, filename: str) -> str:
    return src_path(date, filename)


def hdf_file_is_in_US(filename: str) -> bool:
    hv_section = filename.split('.')[2]
    h, v = [int(x) for x in hv_section.replace('h', '').split('v')]
    return (US_H_MIN <= h <= US_H_MAX) and (US_V_MIN <= v <= US_V_MAX)


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


def download_file(url: str) -> None:
    # url pattern for each file =
    # {ROOT_URL}/yyyy.mm.dd/MCD19A2.A{YYYYDDD}.h{HH}v{VV}.006.{garbage}.hdf
    pass


if __name__ == "__main__":
    all_dates = get_all_dates()
    example_list_of_hdf_files = files_on_date('2019.07.01')
