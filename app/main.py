import json
import uvicorn

from os import path, listdir, walk, stat, chdir
from os.path import isfile, join, exists, splitext, isdir

from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

app = FastAPI()

ROOT_DIR = ""
FILES_ROOT = "/files"


def set_root_dir(rd: str):
    global ROOT_DIR
    ROOT_DIR = FILES_ROOT
    if rd:
        if rd[0] == "/":
            ROOT_DIR = "".join([FILES_ROOT, rd])
        else:
            ROOT_DIR = join(FILES_ROOT, rd)
    print("ROOT_DIR:", ROOT_DIR)


@app.get("/")
def listfiles(q: str = Query(None)):
    path = join(ROOT_DIR, q) if q else ROOT_DIR
    items = get_path_items(path)
    items_json_encoded = jsonable_encoder(items)
    resp = {"count": len(items), "items": items_json_encoded}
    return JSONResponse(content=resp)


def get_path_items(path: str):
    """
    Get directory or file details at the given filepath
    """
    if not exists(path):
        host_path = get_host_path(path)
        raise HTTPException(
            status_code=404,
            detail="The path `{}` does not exist or you don't have permissions to access it.".format(
                host_path
            ),
        )

    _, file_extension = splitext(path)
    if file_extension and file_extension != ".txt":
        raise HTTPException(status_code=404, detail="Can only read .txt files")

    items = []
    if isdir(path):
        items = get_dir(path)
    else:
        items = get_file(path)

    return items


def get_dir(path: str):
    """
    Get list of items in a directory at the given filepath
    """
    items = listdir(path)
    dir_list = []
    for item in items:
        item_path = join(path, item)
        owner, size, permissions = get_stats(item_path)
        dir_list.append(
            {"name": item, "owner": owner, "size": size, "permissions": permissions}
        )

    return dir_list


def get_file(path: str):
    """
    Get file's info and content
    """
    content = None
    with open(path) as f:
        content = f.read()

    filename, _ = splitext(path)
    owner, size, permissions = get_stats(path)
    return [
        {
            "name": filename,
            "owner": owner,
            "size": size,
            "permissions": permissions,
            "content": content,
        }
    ]


def get_stats(path: str):
    """
    Get item's (file or dir) stats for a given filepath
    """
    if not exists(path):
        return None, None, None

    item_stat = stat(path)
    return item_stat.st_uid, item_stat.st_size, item_stat.st_mode


def get_host_path(path):
    """
    Strip container's root path from the given filepath to reflect host's root path
    """
    return path.replace(FILES_ROOT, "", 1)


if __name__ == "__main__":
    rd = input("Welcome. Please specify a root directory: ")
    set_root_dir(rd)
    uvicorn.run(app, port=8000, host="0.0.0.0")
