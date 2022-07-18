import os
import random

import consts
import file_helper
import web_helper


def check_for_update() -> int:
    """
    Checks if there is an update available.
    """
    data = web_helper.request(
        consts.kUpdateURL,
        method="GET",
        data_as_json=False,
    )

    if data.status == 404:
        # If the server returns a 404, there is no update available.
        return 0

    current_update_file = file_helper.ReadFile(os.path.join(consts.kConfigDirectory, ".update"))
    if len(current_update_file) <= 0:
        # If the current update file is empty, there is an update available.
        return 1

    try:
        current_update_version = int(current_update_file[0])
    except ValueError:
        # If the update file is not a number, there is an update available.
        return 1

    if current_update_version < int(data.body):
        # If the current update version is less than the update version, there is an update available.
        return 1

    # No update available.
    return 0
