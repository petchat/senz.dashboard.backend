# coding: utf-8

from flask import Flask, session, render_template, request, redirect
from itsdangerous import Signer
from views.panel import panel
from views.restapi import restapi
from views.dashboard import dashboard
from views.integration import integration
from views.settings import settings
from views.login import login_view
from datetime import timedelta
from models import Developer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
signer = Signer(app.config['SECRET_KEY'])
app.permanent_session_lifetime = timedelta(hours=1)

# 动态路由
app.register_blueprint(panel)
app.register_blueprint(dashboard)
app.register_blueprint(integration)
app.register_blueprint(settings)
app.register_blueprint(login_view)
app.register_blueprint(restapi)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        app_id = request.form.get('app_id')
        session['app_id'] = app_id
        return redirect('/')

    username = session.get('username')
    app_id = session.get('app_id', None)
    app_list = []
    if session.get('session_token'):
        app_list = session.get('app_list', None)
        if not app_list:
            developer = Developer()
            developer.session_token = session.get('session_token')
            app_list = developer.get_app_list()
            session['app_list'] = app_list
    return render_template('index.html',
                           username=username,
                           app_id=app_id,
                           app_list=app_list)


@app.template_filter('translate_motion')
def translate_motion(s):
    library = {'motionCommuting': '乘车',   'motionWalking': '走路', 'motionSitting': '静坐',
               'motionBiking': '骑车', 'motionRunning': '跑步'}
    return library[s]


@app.template_filter('translate_context')
def translate_context(s):
    library = {'contextAtHome': '在家', 'contextCommutingWork': '上班路上', 'contextAtWork': '在公司',
               'contextCommutingHome': '回家路上', 'contextWorkingInCBD': '商圈工作中',
               'contextStudyingInSchool': '学校上课中', 'contextWorkingInSchool': '学校工作中',
               'contextOutdoorExercise': '户外锻炼', 'contextIndoorExercise': '室内锻炼',
               'contextDinningOut': '在餐厅吃饭', 'contextTravelling': '旅游', 'contextShortTrip': '郊游',
               'contextInParty': '聚会', 'contextWindowShopping': '逛街', 'contextAtCinema': '看电影',
               'contextAtExhibition': '展览会', 'contextAtPopsConcert': '演唱会', 'contextAtTheatre': '戏剧',
               'contextAtClassicsConcert': '音乐会'}
    return library[s]
