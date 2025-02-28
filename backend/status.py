import json


def update_status(
        update_session,
):
    return json.dumps(
        {
            "session":  update_session
        },
        ensure_ascii=False
    )