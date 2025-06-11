from flask import Flask
from routes.LoginPage import login_bp
from routes.RegisterPage import register_bp
from routes.Frame import frame_bp
from routes.HomePage import home_bp
from routes.GoodPage import good_bp
from routes.GoodDetail import goodDetail_bp
from routes.ClientPage import clientPage_bp
from dbconfig.dbconnect import db, DB_URI 
from dbconfig.redisconfig import cache
from dbconfig.Scheduler import scheduler
from dbconfig.Scheduler import flush_click_counts
import os
from flask_cors import CORS

# 創建 Flask 應用實例
app = Flask(__name__)

# 設定應用密鑰（用於會話、JWT等）
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')

# 設定 SQLAlchemy 連線
app.config['SQLALCHEMY_ECHO'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 初始化 SQLAlchemy
db.init_app(app)

# 註冊藍圖（Blueprint）- 這將引入 login_bp 中定義的所有路由
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(frame_bp)
app.register_blueprint(home_bp)
app.register_blueprint(good_bp)
app.register_blueprint(goodDetail_bp)
app.register_blueprint(clientPage_bp)


# 啟用 CORSa
CORS(app)

# 定義根路由 - 用來檢查 API 服務是否正常運行
@app.route("/")
def home():
    """首頁端點，返回簡單訊息表示 API 服務運行中"""
    return {"message": "API Server is running"}

@app.route("/admin/trigger-flush") # 用來測試排程 上線前記得刪除
def trigger_flush():
      flush_click_counts()
      return {"message": "flush_click_counts triggered"}

# 主程序入口點
if __name__ == "__main__":
    scheduler.start()
    app.run(debug=True, host="0.0.0.0", port=5000)
