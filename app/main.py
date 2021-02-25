import json
import uvicorn

from os import path, listdir, walk, stat
from os.path import isfile, join, exists, splitext, isdir

from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI()

HOME_DIR = ""
FILES_ROOT = "/usr/files"


def set_home_dir(dir:str):
    global HOME_DIR
    HOME_DIR = FILES_ROOT
    if dir:
        HOME_DIR = "{}/{}".format(HOME_DIR, dir)
    print("HOME_DIR is: {}".format(HOME_DIR))


@app.get("/")
def listfiles(q:str = Query(None)):
    path = HOME_DIR
    if q:
        path = join(HOME_DIR, q)
    files = get_details(path)
    return JSONResponse(content=files)


def get_details(path):
    print("List files at: {}".format(path))
    
    filename, file_extension = splitext(path)
    if file_extension and file_extension != ".txt":
        raise HTTPException(status_code=404, detail="Can only read .txt files")
    
    if not exists(path):
        raise HTTPException(
            status_code=404, detail="The path `{}` does not exist.".format(path)
        )

    if isdir(path):
        return get_dir(path)
    else:
        return get_file(path)


def get_dir(path):
    items = listdir(path)
    items_list = []
    for item in items:
        item_path = join(path, item)
        item_stat = stat(item_path)

        owner, size, permissions = None, None, None
        if item_stat:
            owner, size, permissions = (
                item_stat.st_uid,
                item_stat.st_size,
                item_stat.st_mode,
            )

        items_list.append({
                "name": item, 
                "owner": owner, 
                "size": size, 
                "permissions": permissions
            }
        )

    return jsonable_encoder(items_list)


def get_file(path):
    filename, file_extension = splitext(path)

    with open(path) as f:
        content = f.read()

    item_stat = stat(path)
    owner, size, permissions = (
        item_stat.st_uid,
        item_stat.st_size,
        item_stat.st_mode,
    )
    return jsonable_encoder(
        {
            "name": filename,
            "owner": owner,
            "size": size,
            "permissions": permissions,
            "content": content,
        }
    )


if __name__ == "__main__":
    dir = input("Welcome. Please specify a root directory:")
    print("OK! " + dir)
    set_home_dir(dir)
    uvicorn.run(app, port=8000, host="0.0.0.0")
