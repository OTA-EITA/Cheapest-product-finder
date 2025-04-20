from celery import shared_task
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc
from ..models.database import engine
from ..models.models import User, Product, Price, PriceAlert
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# ロガーの設定
logger = logging.getLogger(__name__)

# データベースセッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@shared_task(name="app.tasks.alert.check_price_alerts")
def check_price_alerts():
    """価格アラートをチェックして、条件を満たす場合は通知を送信するタスク"""
    logger.info("Starting price alert check...")
    
    # データベースセッションの作成
    db = SessionLocal()
    
    try:
        # アクティブな価格アラートを取得
        alerts = db.query(PriceAlert).filter(PriceAlert.is_active == True).all()
        logger.info(f"Found {len(alerts)} active price alerts")
        
        notification_count = 0
        
        for alert in alerts:
            try:
                # 最新の価格情報を取得
                latest_price = db.query(Price).filter(
                    Price.product_id == alert.product_id
                ).order_by(desc(Price.timestamp)).first()
                
                if not latest_price:
                    logger.warning(f"No price information found for product {alert.product_id}")
                    continue
                
                # ユーザーと商品情報を取得
                user = db.query(User).filter(User.id == alert.user_id).first()
                product = db.query(Product).filter(Product.id == alert.product_id).first()
                
                if not user or not product:
                    logger.warning(f"User or product not found for alert {alert.id}")
                    continue
                
                # 目標価格以下になったかチェック
                if latest_price.total_price <= alert.target_price:
                    logger.info(f"Price alert triggered for user {user.id} on product {product.id}")
                    
                    # 通知を送信
                    send_alert_notification(
                        user.email,
                        product.name,
                        product.url,
                        alert.target_price,
                        latest_price.total_price,
                        latest_price.timestamp
                    )
                    
                    # アラートを非アクティブに設定（一度通知したら終了）
                    alert.is_active = False
                    db.commit()
                    
                    notification_count += 1
            
            except Exception as e:
                logger.error(f"Error processing alert {alert.id}: {str(e)}")
                continue
        
        logger.info(f"Price alert check completed. Notifications sent: {notification_count}")
        
        return {
            "success": True,
            "notifications_sent": notification_count,
            "total_alerts": len(alerts)
        }
    
    except Exception as e:
        logger.error(f"Error in check_price_alerts task: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()

def send_alert_notification(email, product_name, product_url, target_price, current_price, timestamp):
    """メールで価格アラート通知を送信"""
    try:
        # メール設定
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER", "your-email@gmail.com")
        smtp_password = os.getenv("SMTP_PASSWORD", "your-app-password")
        
        sender_email = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
        
        # メールの作成
        message = MIMEMultipart("alternative")
        message["Subject"] = f"【最安値アラート】{product_name}が目標価格に達しました"
        message["From"] = sender_email
        message["To"] = email
        
        # テキスト形式の本文
        text = f"""
        商品の価格が目標価格に達しました！

        商品名: {product_name}
        現在価格: {current_price}円
        目標価格: {target_price}円
        確認日時: {timestamp.strftime('%Y年%m月%d日 %H:%M')}

        商品を確認する: {product_url}

        ※このメールは自動送信されています。返信はできません。
        最安値検索アプリより
        """
        
        # HTML形式の本文
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ padding: 20px; max-width: 600px; margin: 0 auto; }}
                .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .price {{ font-size: 24px; color: #E53935; font-weight: bold; }}
                .button {{ background-color: #4CAF50; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; }}
                .footer {{ font-size: 12px; color: #757575; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>最安値アラート</h1>
                </div>
                <div class="content">
                    <p>商品の価格が目標価格に達しました！</p>
                    
                    <h2>{product_name}</h2>
                    
                    <p>現在価格: <span class="price">{current_price}円</span></p>
                    <p>目標価格: {target_price}円</p>
                    <p>確認日時: {timestamp.strftime('%Y年%m月%d日 %H:%M')}</p>
                    
                    <p style="margin-top: 30px;">
                        <a href="{product_url}" class="button">商品を確認する</a>
                    </p>
                    
                    <div class="footer">
                        <p>このメールは自動送信されています。返信はできません。<br>最安値検索アプリより</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # テキストとHTMLパートの追加
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        
        message.attach(part1)
        message.attach(part2)
        
        # メール送信（開発環境ではログに出力するだけ）
        if os.getenv("ENVIRONMENT", "development") == "production":
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(sender_email, email, message.as_string())
                logger.info(f"Price alert email sent to {email}")
        else:
            logger.info(f"[DEVELOPMENT] Would send price alert email to {email}")
            logger.info(f"Email subject: {message['Subject']}")
            logger.info(f"Email body: {text}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error sending alert notification: {str(e)}")
        return False
