import os

from backend import consts, web_helper
from backend.file_helper import ReadFile


def check_for_update() -> int:
    """
    Checks if there is an update available.
    """
    data = web_helper.request(
        "https://raw.githubusercontent.com/Apollys/PoEDynamicLootFilter/master/config/.update",
        method="GET",
        data_as_json=False,
    )

    if data.status == 404:
        print("Update available.")
        return 1

    current_update_file = ReadFile(os.path.join(consts.kConfigDirectory, ".update"))
    if len(current_update_file) <= 0:
        raise Exception("No update file found.")

    try:
        current_update_version = int(current_update_file[0])
    except ValueError:
        raise Exception("Invalid update file.")

    if current_update_version < int(data.body):
        print("Update available.")
        return 1

    return 0
