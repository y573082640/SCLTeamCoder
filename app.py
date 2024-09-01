from flask import Flask, request, jsonify
from scl_team_coder import run_exps_service
import time
import jieba
jieba.initialize()
app = Flask(__name__)


@app.route('/', methods=['POST'])
def generate_code():
    data = request.get_json()
    response = run_exps_service(data)
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)