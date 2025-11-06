from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/ping')
def ping():
    return 'pong', 200

@app.route('/invocations', methods=['POST'])
def invocations():
    data = request.get_json()
    # placeholder: echo the input
    return jsonify({'received': data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
