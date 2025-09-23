from huey import RedisHuey

# queue khusus module 'authentication'
huey = RedisHuey('authentication', host='127.0.0.1', port=6379)

@huey.task()
def send_welcome_email(user_id):
    print(f"[TASK] Sending welcome email to user {user_id}")
