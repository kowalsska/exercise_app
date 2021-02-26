import os
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

import util


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


@app.get(
    "/",
    response_model=Response,
    responses={
        200: {
            "description": "Success",
        },
        400: {
            "description": "Bad request",
            "content": {
                "application/json": {"example": {"details": "Can only read .txt files"}}
            },
        },
        404: {
            "description": "Not found",
            "content": {
                "application/json": {
                    "example": {
                        "details": "The path does not exist or you don't have permissions to access it"
                    }
                }
            },
        },
    },
)
def list_items(q: str = Query(None)):
    path = safe_path_join(path=q, root=os.environ["ROOT_DIR"])
    items = get_path_items(path)
    items_json_encoded = jsonable_encoder(items)

    resp = {
        "path": get_host_path(path),
        "count": len(items),
        "items": items_json_encoded,
    }
    return JSONResponse(content=resp)


class AddFile(BaseModel):
    name: str
    owner: Optional[int]
    permissions: Optional[int]
    content: Optional[str]


@app.post(
    "/file",
    response_model=Item,
    responses={
        200: {
            "description": "Success",
        },
        403: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": [
                        {"details": "New file requires a name"},
                        {"details": "Specified location is not a directory"},
                    ]
                }
            },
        },
    },
)
def add_file(item: AddFile, q: str = Query(None)):
    path = safe_path_join(path=q, root=os.environ["ROOT_DIR"])
    if os.path.isdir(path):
        filepath = util.write_file(path, item)
        resp = util.get_file(filepath)
        return JSONResponse(content=jsonable_encoder(resp))
    elif not item.name:
        raise HTTPException(status_code=403, detail="New file requires a name.")
    else:
        raise HTTPException(
            status_code=403, detail="Specified location is not a directory."
        )


@app.put(
    "/file",
    response_model=Item,
    responses={
        200: {
            "description": "Success",
        },
        403: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {"details": "Failed to update or create a file"},
                }
            },
        },
    },
)
def update_file(item: AddFile, q: str = Query(None)):
    filepath = os.path.join(q, item.name)
    path = safe_path_join(path=q, root=os.environ["ROOT_DIR"])
    filepath = util.write_file(path, item)

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=403, detail="Failed to update or create a file."
        )

    resp = util.get_file(filepath)
    return JSONResponse(content=jsonable_encoder(resp))


class DeleteFile(BaseModel):
    name: str


@app.delete(
    "/file",
    response_model=Item,
    responses={
        200: {
            "description": "Success",
        },
        404: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {"details": "File does not exists"},
                }
            },
        },
    },
)
def delete_file(item: DeleteFile, q: str = Query(None)):
    filepath = os.path.join(q, item.name)
    safe_path = safe_path_join(path=filepath, root=os.environ["ROOT_DIR"])
    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="File does not exists.")

    resp = util.get_file(safe_path)
    os.remove(safe_path)
    return JSONResponse(content=jsonable_encoder(resp))


class UpdateDir(BaseModel):
    name: str


@app.post(
    "/dir",
    response_model=Response,
    responses={
        200: {
            "description": "Success",
        },
        403: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {"details": "This directory already exists"},
                }
            },
        },
    },
)
def add_dir(item: UpdateDir, q: str = Query(None)):
    safe_path = safe_path_join(path=q, root=os.environ["ROOT_DIR"])
    path = util.make_dir(safe_path, item.name)
    items = util.get_dir(path)
    items_json_encoded = jsonable_encoder(items)
    resp = {
        "path": get_host_path(path),
        "count": len(items),
        "items": items_json_encoded,
    }
    return JSONResponse(content=resp)


@app.delete(
    "/dir",
    response_model=Response,
    responses={
        200: {
            "description": "Success",
        },
        400: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {
                        "details": "This directory is not empty. Remove its contents first"
                    },
                }
            },
        },
        404: {
            "description": "Not found",
            "content": {
                "application/json": {
                    "example": {"details": "This directory doesn't exist"},
                }
            },
        },
    },
)
def delete_dir(item: UpdateDir, q: str = Query(None)):
    safe_path = safe_path_join(path=q, root=os.environ["ROOT_DIR"])
    dir_path = os.path.join(safe_path, item.name)
    if not os.path.isdir(dir_path):
        raise HTTPException(status_code=404, detail="This directory doesn't exist.")

    items = util.get_dir(dir_path)
    items_json_encoded = jsonable_encoder(items)
    resp = {
        "path": get_host_path(dir_path),
        "count": len(items),
        "items": items_json_encoded,
    }
    util.remove_dir(dir_path)
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
        raise HTTPException(status_code=403, detail="Can only read .txt files")

    items = []
    if os.path.isdir(path):
        items = util.get_dir(path)
    else:
        items = util.get_file(path)

    return items


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
    Sets env var ROOT_DIR using the input provided by the user
    """
    safe_root_dir = safe_path_join(path=rd)
    os.environ["ROOT_DIR"] = safe_root_dir


if __name__ == "__main__":
    rd = input("Welcome. Please specify a root directory: ")
    set_root_dir(rd)
    uvicorn.run(app, port=8000, host="0.0.0.0")
