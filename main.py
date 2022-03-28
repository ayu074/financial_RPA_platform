import os
import sys
import re
ROOT_PATH = re.search('(.*)\\\\', os.path.abspath(__file__)).group(1)
sys.path.append(ROOT_PATH + r'\venv\Lib\site-packages')

import logging
import time

import filterFunction
import mainView
import app_vatCollection
import app_monthlyClosing

from flask import Flask, request, redirect
from SqlFunction import init_all_db


def set_file_log_handler():
    date_format = time.strftime('%Y%m%d')
    file_name = ROOT_PATH + '\\log\\flask_log_' + date_format + '.log'
    flask_file_handler = logging.FileHandler(file_name)
    logging_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    flask_file_handler.setFormatter(logging_format)
    return flask_file_handler


# 初始化数据库
init_all_db()

app = Flask(__name__)

# 注册蓝图
app.register_blueprint(mainView.mainView)  # 主页等相关路由
app.register_blueprint(app_vatCollection.vatCollection, url_prefix='/vatCollection')  # 增值税收缴
app.register_blueprint(app_monthlyClosing.monthlyClosing, url_prefix='/monthlyClosing')

# 添加模板过滤器
app.add_template_filter(filterFunction.format_number, 'thousand')

# 允许中文显示
app.config['JSON_AS_ASCII'] = False

# 添加日志工具
default_logger = logging.getLogger('werkzeug')
my_logger = logging.getLogger(app.logger.name)
tornado_access_log = logging.getLogger('tornado.access')
tornado_app_log = logging.getLogger('tornado.application')
tornado_gen_log = logging.getLogger('tornado.genneral')
logging.basicConfig(level=logging.INFO)
default_logger.addHandler(set_file_log_handler())
my_logger.addHandler(set_file_log_handler())
tornado_access_log.addHandler(set_file_log_handler())
tornado_app_log.addHandler(set_file_log_handler())
tornado_gen_log.addHandler(set_file_log_handler())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='80')