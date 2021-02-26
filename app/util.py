import os
from fastapi import HTTPException


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


def remove_dir(path):
    try:
        os.rmdir(path)
    except OSError:
        raise HTTPException(
            status_code=404,
            detail="This directory is not empty. Remove its contents first.",
        )


def make_dir(path, name):
    dir_path = os.path.join(path, name)
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        raise HTTPException(status_code=404, detail="This directory already exists.")
    else:
        return dir_path


def write_file(path, item):
    filepath = os.path.join(path, item.name)
    with open(filepath, "a") as f:
        if item.content:
            f.write(item.content)
        if item.permissions:
            os.chmod(path, item.permissions)
        if item.owner:
            os.chown(path, item.owner, -1)
    return filepath
