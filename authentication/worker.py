from huey import RedisHuey

huey = RedisHuey(name="auth_queue")

@huey.task()
def send_welcome_email(user_id):
    print(f"Send welcome email to user {user_id}")
