import requests
from models import Developer
from flask import Blueprint, render_template, request, session

panel = Blueprint('panel', __name__, template_folder='templates')


@panel.route('/panel', methods=['GET', 'POST'])
def show():
    app_id = 'demo55bc5d8e00b0cb9c40dec37b'
    if 'app_list' in session and 'tracker_list' in session:
        app_list = session.get('app_list')
        tracker_list = session.get('tracker_list')
    else:
        developer = Developer()
        developer.session_token = session.get('session_token')
        tracker_list = developer.get_tracker_of_app(app_id)

        developer.get_app_list()
        app_list = developer.app_list
        session['app_list'] = app_list
        session['tracker_list'] = tracker_list

    app_id = session.get('app_id', None)

    motion_dict = {'motionSitting': 0, 'motionWalking': 3, 'motionRunning': 4, 'motionBiking': 2, 'motionCommuting': 1}
    context_list = ['contextAtHome', 'contextCommutingWork', 'contextAtWork', 'contextCommutingHome',
                    'contextWorkingInCBD', 'contextStudyingInSchool', 'contextWorkingInSchool',
                    'contextOutdoorExercise', 'contextIndoorExercise', 'contextDinningOut', 'contextTravelling',
                    'contextShortTrip', 'contextInParty', 'contextWindowShopping', 'contextAtCinema',
                    'contextAtExhibition', 'contextAtPopsConcert', 'contextAtTheatre', 'contextAtClassicsConcert']
    if request.method == 'POST':
        event = request.form.get('type')
        val = request.form.get('val')
        if event and val:
            print event, val
            headers = {"X-AVOSCloud-Application-Id": "wsbz6p3ouef94ubvsdqk2jfty769wkyed3qsry5hebi2va2h",
                       "X-AVOSCloud-Application-Key": "6z6n0w3dopxmt32oi2eam2dt0orh8rxnqc8lgpf2hqnar4tr"}
            payload = {"userId": "559b8bd5e4b0d4d1b1d35e88", "type": event, "val": val}
            requests.post("https://leancloud.cn/1.1/functions/notify_new_details",  headers=headers, data=payload)
    return render_template('panel/panel.html',
                           username=session.get('username'),
                           motion_dict=motion_dict,
                           context_list=context_list,
                           tracker_list=tracker_list,
                           app_id=app_id,
                           app_list=app_list)

