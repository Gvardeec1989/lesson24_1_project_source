import os
import re
from typing import Iterator, List, Any

from flask import Flask, Response, request, abort
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def do_cmd(cmd: str, value: str, data: Iterator) -> List[Any]:
    if cmd == 'filter':
        result = list(filter(lambda record: value in record, data))
    elif cmd == 'map':
        result = list(map(lambda record: record.split()[int(value)], data))
    elif cmd == 'unique':
        result = list(set(data))
    elif cmd == 'sort':
        reverse = (value == 'desc')
        result = list(sorted(data, reverse=reverse))
    elif cmd == 'limit':
        result = list(data[:int(value)])
    elif cmd == 'regex':
        regex = re.compile(value)
        result = list(filter(lambda x: regex.search(x), data))
    else:
        raise BadRequest
    return result


@app.route("/perform_query", methods=["POST", "GET"])
def perform_query() -> Response:
    cmd_1 = request.args.get('cmd1')
    val_1 = request.args.get('value1')
    cmd_2 = request.args.get('cmd2')
    val_2 = request.args.get("value2")
    file_name = request.args.get("file_name")

    if not(cmd_1 and val_1 and file_name):
        abort, 400

    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        return abort(400)

    with open(file_path) as file:
        result = do_cmd(cmd_1, val_1, file)
        if cmd_2 and val_2:
            result = do_cmd(cmd_2, val_2, file)
        result = "\n".join(result)

    return app.response_class(result, content_type="text/plain")


if __name__ == "__main__":
    app.run()
