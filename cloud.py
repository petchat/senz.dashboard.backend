# coding: utf-8

from leancloud import Engine, Query, Object
from app import app

engine = Engine(app)


@engine.define
def post_static_info(**params):
    if 'userId' in params and 'staticInfo' in params:
        user_id = params['userId']
        staticinfo = params['staticInfo']
        parse_dict = parse_static_info(staticinfo)
        return updata_backend_info(user_id, parse_dict)
    else:
        return False


@engine.define
def post_location_info(**params):
    if 'userId' in params and 'location' in params:
        user_id = params['userId']
        location = params['location']
        parse_dict = parse_location_info(location)
        return updata_backend_info(user_id, parse_dict)
    else:
        return False


@engine.define
def post_context_info(**params):
    if 'userId' in params and 'context' in params:
        user_id = params['userId']
        context = params['location']
        parse_dict = parse_context_info(context)
        return updata_backend_info(user_id, parse_dict)
    else:
        return False


def parse_static_info(staticinfo):
    ret_dict = {}
    for key, value in staticinfo.items():
        if isinstance(value, dict):
            ret_dict[key] = sorted(value.items(), key=lambda value: -value[1])[0][0]
        elif isinstance(value, float):
            if key == 'gender':
                ret_dict[key] = 'male' if value > 0 else 'female'
            else:
                ret_dict[key] = 'yes' if value > 0 else 'no'
    print ret_dict
    return ret_dict


def parse_location_info(location):
    ret_dict = {}
    return ret_dict


def parse_context_info(context):
    ret_dict = {}
    return ret_dict


def updata_backend_info(user_id, parse_dict):
    # get user Object
    query = Query(Object.extend('_User'))
    query.equal_to('objectId', user_id)
    user = query.find()[0]

    # get app Object
    query = Query(Object.extend('BindingInstallation'))
    query.equal_to('user', user)
    result_list = query.find()
    app_set = set()
    for result in result_list:
        app_set.add(result.attributes['application'].id)
    app_id_list = list(app_set)

    for app_id in app_id_list:
        query = Query(Object.extend('Application'))
        query.equal_to('objectId', app_id)
        app = query.find()[0]

        table_dash = Object.extend('DashboardSource')
        query = Query(table_dash)
        query.equal_to('app', app)
        query.equal_to('user', user)
        dst_table = query.find()
        if not dst_table:
            dst_table = table_dash()
        else:
            dst_table = dst_table[0]

        dst_table.set('app', app)
        dst_table.set('user', user)
        for key, value in parse_dict.items():
            if value:
                dst_table.set(key, value)
        dst_table.save()
        return True
