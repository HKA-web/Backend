from huey import RedisHuey
from config.settings import REDIS_URL, CONFIG

worker_conf = CONFIG.get('workers', {}).get('sample', {})

queue_name = worker_conf.get('queue', 'sample_queue')
num_workers = worker_conf.get('workers', 1)

huey = RedisHuey(queue_name, url=REDIS_URL)

@huey.task()
def welcome():
    print(f'[INFO] Welcome task on queue={queue_name}')
