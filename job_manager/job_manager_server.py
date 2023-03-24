from flask import Flask, request, jsonify
from job_tasks import word_count, celery_app
from celery.result import AsyncResult

app = Flask(__name__)


@app.route('/count', methods=["POST"])
def count():
    try:
        data = request.get_json()
        if data['text']:
            text = data['text']
            result = word_count.delay(text)
            return jsonify({"id": result.id}), 200
        else:
            return jsonify({"message": "Invalid Input"}), 400
    except KeyError:
        return jsonify({"message": "'text' attribute is not given in the input. Try again"}), 400
    except ValueError:
        return jsonify({"message": "invalid JSON"}), 400


@app.route('/status/<string:id>', methods=['GET'])
def status(id):
    if not id:
        return jsonify({"message": "Invalid Url input. Please give some task ID."}), 400

    try:
        res = AsyncResult(id, app=celery_app)
        if res.status == "SUCCESS":
            return jsonify({"job"+res.status}), 200
        elif (res.status == "PENDING"):
            return jsonify({"error": res.status+"The job is running. Try later."}), 400
        elif res.status == "FAILED":
            return jsonify({"status": res.status+"Task has failed"}), 400
        return jsonify({"message": "Try again"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 400
