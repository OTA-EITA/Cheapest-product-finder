#!/bin/bash
set -e

# データベースの初期化
python -c "
from database.base import Base, engine
Base.metadata.create_all(bind=engine)
print('データベースの初期化が完了しました。')
"

# サービスの種類に応じて異なるコマンドを実行
case "$1" in
    backend)
        uvicorn main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    worker)
        celery -A services.tasks worker --loglevel=info
        ;;
    *)
        exec "$@"
        ;;
esac
