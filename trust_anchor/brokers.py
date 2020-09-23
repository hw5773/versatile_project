from flask import Flask, url_for
from flask import request
from flask import jsonify
#from flask import json
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

app = Flask(__name__)

@app.route('/brokers', methods = ['GET'])
def get_brokers():
    if request.method == 'GET':
        result = {"brokers":\
                [{"name":"www.versatile-broker-1.com"},\
                {"name":"www.versatile-broker-2.com"}]}

        answer = json.dumps(result)
        return answer

if __name__ == '__main__':

    app.run(host="147.46.114.86", port=3333)
    

