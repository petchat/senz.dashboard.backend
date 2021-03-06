# coding: utf-8

from leancloud import Engine, Query, Object
from datetime import datetime
# from application.common.util import post_panel_data
from application.common.util import translate
from flask import json
from os.path import dirname, join
from server import app
import time

engine = Engine(app)
DashboardStatistics = Object.extend("DashboardStatistics")
BindingInstallation = Object.extend('BindingInstallation')
DashboardSource = Object.extend('DashboardSource')


@engine.define
def post_obj_from_timeline(name, obj):
    if name == 'UserLocation':
        parse_dict = parse_location_info(obj)
    elif name == 'HomeOfficeStatus':
        parse_dict = parse_home_office_info(obj)
    elif name == 'UserInfoLog':
        parse_dict = parse_static_info(obj)
    elif name == 'UserMotion':
        parse_dict = parse_motion_info(obj)
    elif name == 'UserEvent':
        parse_dict = parse_event_info(obj)
    elif name == 'UserActivity':
        parse_dict = parse_avtivity_info(obj)
    else:
        parse_dict = {}
    return updata_backend_info(parse_dict)


def parse_motion_info(motion_obj):
    ret_dict = {}
    user_id = motion_obj.get('user').get('objectId')
    ret_dict['user_id'] = user_id
    timestamp = motion_obj.get('timestamp') or None
    motion_prob = motion_obj.get('motionProb') or {}
    motion_prob = sorted(filter(lambda x: x, motion_prob.items()), key=lambda v: -v[1])
    motion = translate(motion_prob[0][0] if motion_prob else "", 'motion_old')
    if motion:
        ret_dict['motion'] = {timestamp:  motion}
        # post_panel_data(tracker=user_id, type='motion', value=motion, timestamp=timestamp)
    return ret_dict


def parse_static_info(info_log):
    ret_dict = {}
    user_id = info_log.get('user').get('objectId')
    ret_dict['user_id'] = user_id
    static_info = info_log.get('staticInfo') or {}
    translation = json.load(file(join(dirname(__file__), 'translate.json')))

    interest = []
    for key, value in static_info.items():
        if key == 'sport' or key in translation.get('interest').keys():
            if key == 'sport':
                interest += value.keys()
            else:
                interest.append(key)
        elif isinstance(value, dict):
            ret_dict[key] = sorted(value.items(), key=lambda v: -v[1])[0][0]
        elif isinstance(value, float):
            if len(key.split('-')) > 1:
                ret_dict[key.split('-')[0]] = key.split('-')[1]
            elif key == 'gender':
                ret_dict[key] = 'male' if value > 0 else 'female'
            else:
                ret_dict[key] = 'yes' if value > 0 else 'no'
    ret_dict['interest'] = list(set(interest))
    return ret_dict


def parse_location_info(location_info):
    ret_dict = {}
    user_id = location_info.get('user').get('objectId')
    location = location_info.get('location')
    province = location_info.get('province')
    city = location_info.get('city')
    street = location_info.get('street')
    poiproblv1 = location_info.get('poiProbLv1') or {}
    poiproblv2 = location_info.get('poiProbLv2') or {}
    timestamp = location_info.get('timestamp') or None

    location_tmp = {
        'timestamp': timestamp,
        'location': location,
        'province': province,
        'city': city,
        'street': street,
        'poiProbLv1': sorted(poiproblv1.items(), key=lambda value: -value[1])[0][0],
        'poiProbLv2': sorted(poiproblv2.items(), key=lambda value: -value[1])[0][0]
    }
    ret_dict['user_id'] = user_id
    ret_dict['location'] = location_tmp
    return ret_dict


def parse_home_office_info(homeoffice_info):
    ret_dict = {}
    user_id = homeoffice_info.get('user_id')
    status = translate(homeoffice_info.get('status'), 'home_office_status_old')
    timestamp = homeoffice_info.get('timestamp')
    expire = homeoffice_info.get('expire')
    expire = (int(expire) - int(timestamp)) / 1000
    ret_dict['user_id'] = user_id
    ret_dict['home_office_status'] = {timestamp: status}
    # if time.time()*1000 - timestamp < 300:
    # post_panel_data(tracker=user_id, type='home_office_status', value=status, timestamp=timestamp, expire=expire)
    return ret_dict


def parse_event_info(event_info):
    ret_dict = {}
    user_id = event_info.get('user').get('objectId') if event_info.get('user') else None
    events = event_info.get('event') or {}
    start_time = event_info.get('startTime')
    end_time = event_info.get('endTime')
    timestamp = (start_time+end_time)/2
    ret_dict['user_id'] = user_id
    event_tmp = sorted(events.items(), key=lambda value: -value[1])
    event = translate(event_tmp[0][0], 'event_old') if event_tmp else None
    if event_info.get('isOnSubway'):
        event = 'contextTakingSubway'
    ret_dict['event'] = {timestamp: event}
    # post_panel_data(tracker=user_id, type='event', value=event, timestamp=timestamp)
    return ret_dict


def parse_avtivity_info(activity_info):
    ret_dict = {}
    user_id = activity_info.get('user_id')
    time_range_start = activity_info.get('time_range_start') or None
    time_range_end = activity_info.get('time_range_end') or None
    time_range_start = time.mktime(datetime.strptime(time_range_start['iso'], '%Y-%m-%dT%H:%M:%S.000Z').timetuple())
    time_range_end = time.mktime(datetime.strptime(time_range_end['iso'], '%Y-%m-%dT%H:%M:%S.000Z').timetuple())
    timestamp = (int(time_range_start*1000) + int(time_range_end*1000)) / 2
    activities = activity_info.get('matched_activities')
    activities = activities[0] if activities else {}
    activity = activities.get('category')
    ret_dict['activity'] = {'category': activity,
                            'timestamp': timestamp}
    ret_dict['user_id'] = user_id
    # post_panel_data(tracker=user_id, type='activity', value=activity, timestamp=timestamp)
    return ret_dict


def to_lean_user(uid):
    user = {
        "__type": "Pointer",
        "className": "_User",
        "objectId": uid
    }
    return user


def to_lean_app(app_id):
    app = {
        "__type": "Pointer",
        "className": "Application",
        "objectId": app_id
    }
    return app


def updata_backend_info(parse_dict):
    user_id = parse_dict['user_id']
    user = to_lean_user(user_id)

    # get app Object
    query = Query(BindingInstallation)
    query.equal_to('user', user)
    result_list = query.find()
    app_set = set()
    for result in result_list:
        app_set.add(result.attributes['application'].id)
    app_id_list = list(app_set)

    ts = int(time.mktime(list(time.localtime()[:3]) + [0*x for x in range(0, 6)]))*1000
    statistic_query = Query(DashboardStatistics)
    statistic_query.equal_to('timestamp', ts)
    statistic = statistic_query.first() if statistic_query.count() else DashboardStatistics()
    statistic.set('timestamp', ts)

    for app_id in app_id_list:
        app = to_lean_app(app_id)
        table_dash = DashboardSource
        query = Query(table_dash)
        query.equal_to('app', app)
        query.equal_to('user', user)
        dst_table = query.find()[0] if query.count() else table_dash()

        dst_table.set('app', app)
        for key, value in parse_dict.items():
            if key is 'user_id':
                dst_table.set('user', user)
            elif key is 'home_office_status':
                home_office_count = statistic.attributes.get('home_office_status') or {}
                home_office_status_tmp = dst_table.get('home_office_status') or {}
                home_office_status = {}
                for item in filter(lambda x: x[0] > str(1416200315), home_office_status_tmp.items()):
                    home_office_status[item[0]] = item[1]

                for k, v in parse_dict['home_office_status'].items():
                    home_office_status[k] = v
                    home_office_count[v] = (home_office_count.get(v) or 0) + 1
                statistic.set('home_office_status', home_office_count)
                dst_table.set('home_office_status', home_office_status)
            elif key is 'event':
                event_count = statistic.attributes.get('event') or {}
                event_tmp = dst_table.get('event') or {}
                event = {}
                for item in filter(lambda x: x[0] > str(1416200315), event_tmp.items()):
                    event[item[0]] = item[1]
                for k, v in parse_dict['event'].items():
                    event[k] = v
                    event_count[v] = (event_count.get(v) or 0) + 1
                statistic.set('event', event_count)
                dst_table.set('event', event)
            elif key is 'motion':
                motion_count = statistic.attributes.get('motion') or {}
                motion_tmp = dst_table.get('motion') or {}
                motion = {}
                for item in filter(lambda x: x[0] > str(1416200315), motion_tmp.items()):
                    if isinstance(item[1], unicode):
                        motion[item[0]] = item[1]
                for k, v in parse_dict['motion'].items():
                    motion[k] = v
                    motion_count[v] = (motion_count.get(v) or 0) + 1
                statistic.set('motion', motion_count)
                dst_table.set('motion', motion)
            elif key is 'location':
                dst_table.set('location', value)

                coordinate = value.get('location')
                coordinate_tmp = dst_table.get('coordinate') or []
                coordinate_tmp.insert(0, coordinate)
                if len(coordinate_tmp) > 1000:
                    coordinate_tmp.pop()
                dst_table.set('coordinate', coordinate_tmp)
            else:
                dst_table.set(key, value)
        dst_table.save()
        statistic.save()
        return True


def count_increase():
    ts = int(time.mktime(list(time.localtime()[:3]) + [0*x for x in range(0, 6)]))
    statistic = DashboardStatistics()
    statistic.set('timestamp', ts)


