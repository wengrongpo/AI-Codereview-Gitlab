import os
from multiprocessing import Process

from dotenv import load_dotenv
from redis import Redis
from rq import Queue

load_dotenv()
queue_driver = os.getenv('QUEUE_DRIVER', 'async')

if queue_driver == 'rq':
    # TODO make queue name dynamic
    queue = Queue('default', connection=Redis(os.getenv('REDIS_HOST', '127.0.0.1'), os.getenv('REDIS_PORT', 6379)))

def handle_queue(function: callable, data: any, gitlab_token: str, gitlab_url: str):
    if queue_driver == 'rq':
        queue.enqueue(function, data, gitlab_token, gitlab_url)
    else:
        process = Process(target=function, args=(data, gitlab_token, gitlab_url))
        process.start()
