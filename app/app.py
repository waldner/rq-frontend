import flask
from flask import request
from flask_cors import CORS

import json
import os
from rq import Queue
from rq.job import Job
import rq.exceptions
from redis import Redis
import redis.exceptions

app = flask.Flask(__name__)
if os.environ['CORS'] == 'true':
  CORS(app)

app.config["DEBUG"] = True

def check_req(req):

    if 'task' not in req or 'params' not in req:
        return False

    return True

def date_format(d):
    if d is None:
        return None
    return d.strftime('%Y-%m-%d %H:%M:%S')

@app.route('/', methods=['POST'])
def home():

    req = request.get_json(force=True, silent=True)

    if req is None or not check_req(req):
        return json.dumps({'status': 'invalid JSON'})

    # we have valid json here
    
    # get queue name, if any
    queue_name = DEFAULT_QUEUE
    if 'queue' in req:
        queue_name = req['queue']

    conn = Redis(REDIS_URL)
    q = Queue(queue_name, connection = conn)

    if 'result_ttl' not in req['params']:
        req['params']['job_ttl'] = DEFAULT_JOB_TTL

    job = q.enqueue(req['task'], **req['params'])

    return json.dumps({'status': 'submitted', 'job_id': job.id})

@app.route('/info', methods=['GET'])
def info():

    job_id = request.args.get('job_id')

    conn = Redis(REDIS_URL)

    try:
        job = Job.fetch(job_id, connection=conn)
    except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
        return json.dumps({'status': 'not_found'})

    # refresh job to get meta stuff - not sure it's needed 
    # as we just did a fetch(), but shouldn't hurt
    job.refresh()

    result = { 'status': job.get_status(),
               'worker_name': job.worker_name,
               'origin': job.origin,
               'func_name': job.func_name,
               'args': job.args,
               'meta': job.meta,
               'is_finished': job.is_finished,
               'is_failed': job.is_failed,
               'kwargs': job.kwargs,
               'result': job.result,
               'enqueued_at': date_format(job.enqueued_at),
               'started_at': date_format(job.started_at),
               'ended_at': date_format(job.ended_at),
               'exc_info': job.exc_info }

    return json.dumps(result, default=str)


REDIS_URL = os.environ['RQ_FRONTEND_REDIS_URL']
DEFAULT_JOB_TTL = os.environ['RQ_FRONTEND_DEFAULT_JOB_TTL']  # used if not specified in request
DEFAULT_QUEUE = os.environ['RQ_FRONTEND_DEFAULT_QUEUE']      # used if not specified in request

app.run(host='0.0.0.0', port=80)

