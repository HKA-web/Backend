from huey import RedisHuey
import yaml
from pathlib import Path
import os

# --- Shared Huey instance ---
BASE_DIR = Path(__file__).resolve().parent.parent
config_path = BASE_DIR / "config.yaml"
with open(config_path, "r") as f:
    CONFIG = yaml.safe_load(f)

redis_url = CONFIG.get("channels", {}).get("redis_url", "redis://127.0.0.1:6379/0")
huey = RedisHuey("authentication", url=redis_url)

# --- Task ---
@huey.task()
def send_welcome_email(user_id):
    print(f"[TASK] Sending welcome email to user {user_id}")
