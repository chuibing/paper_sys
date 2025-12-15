# user/views.py
import re
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, login_user
from .models import User, Role
from .repositories import get_college_by_id, username_exists, create_user , get_user_by_username, get_all_colleges

blueprint = Blueprint("user", __name__, url_prefix="/user")
# ===== 1.学院列表 API =====
@blueprint.route("/api/colleges", methods=["GET"])
def colleges_api():
    try:
        colleges = get_all_colleges()
        return jsonify({
            "code": 200,
            "message": "获取学院列表成功",
            "data": colleges
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取学院失败: {e}")
        return jsonify({
            "code": 500,
            "message": "获取学院列表失败"
        }), 500

# ===== 2.登录 API =====
@blueprint.route("/api/login", methods=["POST"])
def login_api():
    data = request.get_json()
    if not data:
        return jsonify({
            "code": 400,
            "message": "请求体必须是 JSON"
        }), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({
            "code": 400,
            "message": "用户名和密码不能为空"
        }), 400

    user = get_user_by_username(username)
    if user and user.check_password(password):
        # 下面可以删去
        role_map = {
            "STUDENT": "/student/home",
            "COLLEGE_ADMIN": "/college_admin/home",
            "UNIVERSITY_ADMIN": "/university_admin/home"
        }
        # redirect_path = role_map.get(user.role.value, "/home")

        # 统一跳转到 HomeView 由前端处理具体页面
        redirect_path = "/user/HomeView" 

        return jsonify({
            "code": 200,
            "message": "登录成功",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "real_name": user.real_name,
                "role": user.role.value,
                "college_id": user.college_id
            },
            "redirect": redirect_path
        }), 200
    else:
        return jsonify({
            "code": 401,
            "message": "用户名或密码错误"
        }), 401

# ===== 3.注册 API=====
@blueprint.route('/api/register', methods=['POST'])
def register_api():
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效 JSON"}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    real_name = data.get('real_name', '').strip()
    role_str = data.get('role', 'student').strip().upper()  # 转为大写
    college_id = data.get('college_id')

    # 验证字段
    if not all([username, password, real_name, college_id]):
        return jsonify({"error": "所有字段都是必填的"}), 400

    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return jsonify({"error": "用户名只能包含字母、数字、下划线，长度 3-20"}), 400

    if role_str not in [r.value for r in Role]:
        return jsonify({"error": f"角色无效，必须是: {[r.value for r in Role]}"}), 400

    # 校验学院和用户名
    try:
        if username_exists(username):
            return jsonify({"error": "用户名已存在"}), 400

        college = get_college_by_id(college_id)
        if not college:
            return jsonify({"error": "学院ID不存在"}), 400

        # 创建用户
        user_id = create_user(username, password, real_name, role_str, college_id)

        return jsonify({
            "code": 201,
            "message": "注册成功",
            "data": {
                "user_id": user_id,
                "username": username,
                "real_name": real_name,
                "role": role_str,
                "college_id": college_id
            }
        }), 201

    except Exception as e:
        current_app.logger.error(f"注册失败: {e}")
        return jsonify({"error": "注册失败，请稍后重试"}), 500