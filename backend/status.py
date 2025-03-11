import json


def update_status(
        update_data,
):
    return json.dumps(
        {
            "data":  update_data
        },
        ensure_ascii=False
    )