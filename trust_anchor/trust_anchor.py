from flask import Flask, url_for
from flask import request
from flask import jsonify
from flask import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def api_lastupdate():
    if request.method == 'GET':
        result = {"flex_id_managers":\
                [{"name":"mbox3","ip":"147.46.114.150","port":"3333"},\
                {"name":"manager","ip":"147.46.113.12","port":"3333"},\
                {"name":"flex","ip":"147.46.22.201","port":"3333"}]}
        return jsonify(result)

if __name__ == '__main__':
    app.run(host="147.46.114.22", port=3333)
