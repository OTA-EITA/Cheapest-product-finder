from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Redisの接続情報
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Celeryアプリの作成
app = Celery(
    'cheapest_price_finder',
    broker=redis_url,
    backend=redis_url,
    include=['app.tasks.price_update', 'app.tasks.alert']
)

# スケジュール設定
app.conf.beat_schedule = {
    'update-prices-every-day': {
        'task': 'app.tasks.price_update.update_all_prices',
        'schedule': crontab(hour=3, minute=0),  # 毎日午前3時に実行
    },
    'check-price-alerts-every-hour': {
        'task': 'app.tasks.alert.check_price_alerts',
        'schedule': crontab(minute=0),  # 毎時0分に実行
    },
}

# タイムゾーン設定
app.conf.timezone = 'Asia/Tokyo'

if __name__ == '__main__':
    app.start()
