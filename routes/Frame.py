from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from dbconfig.dbconnect import db
from models.models import Product

frame_bp = Blueprint("frame", __name__, url_prefix="/frame")

# /frame/search 搜尋商品 (使用 SQLAlchemy ORM)
@frame_bp.route("/search", methods=["POST"])
def search_products():
    data = request.get_json()
    keyword = data.get("keyword", "").strip()
    
    if not keyword:
        return jsonify({"message": "請提供搜尋關鍵字"}), 400

    try:
        # 使用 SQLAlchemy 進行查詢
        pname = data.get("pname", "").strip()
        brand = data.get("brand", "").strip()
        products = Product.query.filter(
            or_(
                Product.pName.ilike(pname),
                Product.brand.ilike(brand)
            )
        ).all() # 取得所有符合條件的 Product 物件

        # 檢查是否有找到結果
        if not products:
            return jsonify({"message": "找不到符合條件的商品"}), 404

        # 將 Product 物件列表轉換為字典列表
        results = []
        for p in products:
            results.append({
                "pId": p.pId,
                "pName": p.pName,
                "brand": p.brand,
                "category": p.category,
                # 確保 price 欄位存在且正確轉換
                "price": float(p.price) if p.price is not None else None, 
                "clickTimes": p.clickTimes,
                "review": p.review
                # 根據您的 Product 模型調整欄位
            })
            
        # 返回查詢結果
        return jsonify({"results": results}), 200

    except Exception as e:
        # 捕捉通用的例外狀況 (例如 SQLAlchemy 查詢錯誤、模型屬性錯誤等)
        print(f"搜尋商品時發生錯誤: {e}")
        # 在生產環境中，避免直接暴露詳細錯誤訊息
        return jsonify({"message": "伺服器內部錯誤，搜尋失敗"}), 500

    # 不需要 finally 區塊來關閉連線，SQLAlchemy 會處理 Session 的生命週期