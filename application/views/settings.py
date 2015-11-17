from flask import Blueprint, render_template, session, request, redirect, url_for
from ..models import Developer


settings = Blueprint('settings', __name__, template_folder='templates')


@settings.route('/settings')
def show():
    if not session.get('session_token'):
        next_url = request.args.get('next') or url_for('index')
        return redirect(url_for('accounts_bp.login') + '?next=' + next_url)
    return redirect(url_for('settings.add_app'))


@settings.route('/create', methods=['GET', 'POST'])
def add_app():
    if not session.get('session_token'):
        return redirect(url_for('accounts_bp.login'))
    if request.method == 'GET':
        app_id = session.get('app_id', None)
        developer = Developer()
        developer.session_token = session.get('session_token')
        username = developer.username()
        app_list = developer.get_app_list()
        return render_template('settings/create.html',
                               username=username,
                               app_id=app_id,
                               app_list=app_list)
    if request.method == 'POST':
        app_name = request.form['app_name']
        user = Developer()
        user.session_token = session.get('session_token')
        app = user.create_new_app(app_name)
        if app:
            return render_template('settings/appkey.html',
                                   app_key=app[1])
        else:
            return redirect(url_for('settings.show'))


@settings.route('/manage', methods=['GET', 'POST'])
def manage_app():
    if not session.get('session_token'):
        return redirect(url_for('accounts_bp.login'))
    if request.method == 'GET':
        app_id = session.get('app_id', None)
        developer = Developer()
        developer.session_token = session.get('session_token')
        username = developer.username()
        app_list = developer.get_app_list()
        return render_template('settings/manage.html',
                               username=username,
                               app_id=app_id,
                               app_list=app_list)
    if request.method == 'POST':
        app_id = request.form.get('app_id')
        if app_id is not '5621fb0f60b27457e863fabb' and app_id is not 'all':
            print "delete", '<', app_id, '>'
            user = Developer()
            user.session_token = session.get('session_token')
            user.delete_app(app_id)
        return redirect(url_for('settings.manage_app'))


@settings.route('/modify')
def modify_app():
    pass
