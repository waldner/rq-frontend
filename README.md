# rq-frontend
Submit jobs to [Redis Queue](https://python-rq.org) from any language using an HTTP API.

# WARNING: work in progress.
### WARNING: I made this after reading just two Flask tutorials. It's surely ugly and can be made better.

This is a quick hack thrown together to let non-python apps and service submit jobs to RQ.

# Getting started

Build the docker image or download it from [Docker Hub](https://hub.docker.com/r/waldner/rq-frontend):

```
# build
docker build -t waldner/rq-frontend .

# download
docker pull waldner/rq-frontend
```

Create a `.env` file with the following content:

```
# where to find redis
RQ_FRONTEND_REDIS_URL=192.168.77.8
# where we want rq-frontend to listen for requests
HTTP_ADDR=192.168.0.1
HTTP_PORT=4356
```

Start the container: `docker-compose up -d`

# Usage

Examples are with curl for simplicity, but of course any language or framework that can do HTTP requests will do.

## Submit a job:

```
$ curl http://192.168.0.1:4356 -d '{"task":"tasks.sampletask", "params": {"result_ttl": 0, "args": [60], "kwargs": { "arg1": "hello", "arg2": "world" }}'
{"status": "submitted", "job_id": "a70eedf2-f121-4a02-bf45-5acd82ec9bc7"}
```

Optionally, a queue name can be specified:

```
$ curl http://192.168.0.1:4356 -d '{"queue": "high", "task":"tasks.sampletask", "params": {"result_ttl": 0, "args": [60], "kwargs": { "arg1": "hello", "arg2": "world" }}'
{"status": "submitted", "job_id": "a70e2d42-f121-4602-bf45-5a7d828c91c7"}
```

The payload JSON must contain two keys: `task` with the name of the task to run as recognized by the workers, and `params` with the values to be passed to the worker when the job is enqueued. The `queue` key is optional, and if missing the default queue named `default` is used to submit the job. In the above example, the `params` part causes the following server-side invocation to enqueue the job:

```
...
job = q.enqueue('tasks.sampletask', result_ttl = 0, args = [60], kwargs = {'arg1': 'hello', 'arg2': 'world' })
```

## Retrieve the status of a job:

```
$ curl -s http://192.168.0.1:4356/info?job_id=a70eedf2-f121-4a02-bf45-5acd82ec9bc7 | jq -r .
{
  "status": "started",
  "func_name": "tasks.sampletask",
  "args": [
    60
  ],
  "meta": {},
  "is_finished": false,
  "is_failed": false,
  "kwargs": {
    "arg1": "hello",
    "arg2": "world"
  },
  "result": null,
  "enqueued_at": "2020-10-10 19:35:05",
  "started_at": "2020-10-10 19:35:05",
  "ended_at": null,
  "exc_info": null
}

```

