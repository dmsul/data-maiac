import os
import socket

PROJECT_NAME = 'data-maiac'

# Check which machine we're on
HOST = socket.gethostname()
if HOST in ('sullivan-10d', 'sullivan-7d', 'DESKTOP-HOME', 'ThinkPad-PC'):
    data_root = "D:\\"
elif HOST in ('ashenfarb-10d', ):
    data_root = "C:\\"
else:
    data_root = r'\\Sullivan-10d\d'

DATA_PATH = os.path.join(data_root, 'Data', PROJECT_NAME)


def data_path(*args):
    return os.path.join(DATA_PATH, *args)


def src_path(*args):
    return data_path('src', *args)
