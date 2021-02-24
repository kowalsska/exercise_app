from typing import Optional

from os import path, listdir, walk
from os.path import isfile, join, exists

from fastapi import FastAPI
import uvicorn

app = FastAPI()

HOME_DIR = ""
FILES_ROOT = "/usr/files"


def set_home_dir(dir):
    global HOME_DIR
    HOME_DIR = FILES_ROOT
    if dir:
        HOME_DIR = "{}/{}".format(HOME_DIR, dir)
    print("HOME_DIR is: {}".format(HOME_DIR))

@app.get("/")
def listfiles():
    print("HOME_DIR is: {}".format(HOME_DIR))
    return get_files(HOME_DIR)


@app.get("/{subdir}")
def listfiles(subdir):
    path = "{}/{}".format(HOME_DIR, subdir)
    return get_files(path)


def get_files(path):
    print("List files at: {}".format(path))
    if exists(path):
        return listdir(path)



if __name__ == '__main__':
    dir = input("Welcome. Please specify a root directory:")
    print("OK! " + dir)
    set_home_dir(dir)
    uvicorn.run(app, port=8000, host="0.0.0.0")