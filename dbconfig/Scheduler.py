from apscheduler.schedulers.background import BackgroundScheduler
from dbconfig.redisconfig import cache
from models.models import Product
from dbconfig.dbconnect import db

# 每30分鐘將 Redis 的點擊數寫回資料庫

def flush_click_counts():
    try:
        updates = []
        for key in cache.scan_iter("click_times:*"):
            pId = key.decode().split(":")[1]
            count = int(cache.get(key))
            if count > 0:
                updates.append((pId, count))
            cache.delete(key)

        # 在commit前先更新最後的點擊次數
        for pId, count in updates:
            db.session.query(Product).filter_by(pId=pId).update(
                {Product.clickTimes: Product.clickTimes + count},
                synchronize_session=False
            )
        db.session.commit()
        print(f"新增商品點擊次數: {pId} - {count}")
        print(f"已將 {len(updates)} 筆 Redis 點擊數寫回資料庫")
    except Exception as e:
        db.session.rollback()
        print(f"排程寫回點擊數時發生錯誤: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(flush_click_counts, 'interval', minutes=30)