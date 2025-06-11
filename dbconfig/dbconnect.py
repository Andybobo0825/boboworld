from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

# 設定 Microsoft SQL Server 連線資訊
DB_USERNAME = "testuser"
DB_PASSWORD = "QWEasd+123"
DB_SERVER = "DESKTOP-8RCNUI2\SQLEXPRESS"
DB_NAME = "DB"
DB_DRIVER = "ODBC Driver 17 for SQL Server"

# 建立 SQLAlchemy 連線字串
# 正確指定 ODBC 驅動程式
DB_URI = f"mssql+pyodbc://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"

# 初始化 SQLAlchemy
db = SQLAlchemy()
engine = create_engine(DB_URI, echo=True)  # echo=True 顯示執行的 SQL 查詢，方便除錯
