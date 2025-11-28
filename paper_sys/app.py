# app.py
from flask import Flask, send_from_directory
from users.views import blueprint  # ← 改成 blueprint
from config import Config
from users.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # 注册蓝图
    app.register_blueprint(blueprint)  # ← 这里也用 blueprint

    # 前端页面路由（保持不变）
    @app.route('/')
    @app.route('/login')
    def login_page():
        return send_from_directory('static', 'LoginView.html')

    @app.route('/student/home')
    def student_home():
        return send_from_directory('static', 'student/HomeView.html')

    @app.route('/college_admin/home')
    @app.route('/university_admin/home')
    def admin_home():
        return send_from_directory('static', 'college_admin/HomeView.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)