#/usr/bin/env python
import json
import os
import sys


from fabric.api import env, task, put, sudo, local, cd, lcd, run, prompt
from fabric.colors import red, green, blue, yellow
from fabric.api import shell_env
from fabric.context_managers import cd, prefix, settings, hide
from fabric.contrib.files import exists


# MINIREFERENCE CONSTANTS
################################################################################
POD_PACKAGE_IDS = {
    "softcover": "0550X0850BWSTDPB060UW444GXX",
    "hardcover": "??",
}




# FILE STORAGE BACKEND
################################################################################
env.hosts = ['52.73.72.76']
env.user = 'ivan'

REMOTE_DIR = "/home/ivan/www/minireference/static/tmp/printables/"
REMOTE_DIR_URL = "https://minireference.com/static/tmp/printables/"


@task
def upload_file(localpath, name=None):
    """
    Upload `localpath` PDF file to file storage server and return public URL.
    """
    filename = os.path.split(localpath)[1]
    assert filename[-3:].lower() == 'pdf', 'Wrong extensions; only PDFs allowed'
    remotefilename = name if name else filename
    remotepath = os.path.join(REMOTE_DIR, remotefilename)
    remote_url = REMOTE_DIR_URL + remotefilename
    if exists(remotepath):
        print(yellow('File already exists, see ') + blue(remote_url))
    else:
        put(localpath, remotepath)
        assert exists(remotepath), f"Remotepath {remotepath} doesn't exist!"
        print(green('File uplaoded to  ') + blue(remote_url))
    return remote_url


@task
def uplaod_book():
    pass  # TODO: read catalog.yaml and upload book files to get `source_url`s
