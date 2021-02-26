import os
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


ROOT_DIR = ""
FILES_ROOT = "/files"


app = FastAPI(
    title="Coding Exercise",
    description="Tiny REST API app for directory traversal",
    version="0.0.1",
)


class Item(BaseModel):
    name: str
    owner: int
    size: int
    permissions: int
    content: Optional[str]


class Response(BaseModel):
    path: str
    count: int
    items: List[Item]


@app.get("/", response_model=Response)
def list_files(q: str = Query(None)):
    path = safe_path_join(path=q, root=ROOT_DIR)
    items = get_path_items(path)
    items_json_encoded = jsonable_encoder(items)

    resp = {
        "path": get_host_path(path),
        "count": len(items),
        "items": items_json_encoded,
    }
    return JSONResponse(content=resp)


def get_path_items(path: str):
    """
    Get directory or file details at the given filepath
    """
    if not os.path.exists(path):
        host_path = get_host_path(path)
        raise HTTPException(
            status_code=404,
            detail="The path `{}` does not exist or you don't have permissions to access it.".format(
                host_path
            ),
        )

    _, file_extension = os.path.splitext(path)
    if file_extension and file_extension != ".txt":
        raise HTTPException(status_code=404, detail="Can only read .txt files")

    items = []
    if os.path.isdir(path):
        items = get_dir(path)
    else:
        items = get_file(path)

    return items


def get_dir(path: str):
    """
    Get list of items in a directory at the given filepath
    """
    items = os.listdir(path)
    dir_list = []
    for item in items:
        item_path = os.path.join(path, item)
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

    filename = os.path.basename(path)
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
    if not os.path.exists(path):
        return None, None, None

    item_stat = os.stat(path)
    return item_stat.st_uid, item_stat.st_size, item_stat.st_mode


def get_host_path(path):
    """
    Strip container's root path from the given filepath to reflect host's root path
    """
    host_path = path.replace(FILES_ROOT, "", 1)
    return host_path if host_path else "/"


def safe_path_join(path: str = None, root: str = FILES_ROOT):
    """
    Unify the path format in case the user prepended a backslash, remove trailing backslash
    """
    if path and path[0] == "/":
        safe_path = "".join([root, path])
    else:
        path = path if path else ""
        safe_path = os.path.join(root, path)

    return safe_path[:-1] if safe_path and safe_path[-1] == "/" else safe_path


def set_root_dir(rd: str):
    """
    Sets global ROOT_DIR using the input provided by the user
    """
    global ROOT_DIR
    ROOT_DIR = safe_path_join(path=rd)


if __name__ == "__main__":
    rd = input("Welcome. Please specify a root directory: ")
    set_root_dir(rd)
    uvicorn.run(app, port=8000, host="0.0.0.0")
