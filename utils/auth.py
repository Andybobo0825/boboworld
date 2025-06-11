from functools import wraps
from flask import request, jsonify
import jwt
import os
from dotenv import load_dotenv
from dbconfig.redisconfig import cache

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid token"}), 403

        token = auth_header.split(" ")[1]
        # 檢查 token 是否在黑名單
        if cache.get(f"blacklist:{token}"):
            return jsonify({"message": "Token 已失效，請重新登入"}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # 將解碼後的用戶資訊作為 current_user 參數傳遞
            return f(current_user=payload, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "驗證令牌已過期"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "無效的驗證令牌"}), 401
    return decorated