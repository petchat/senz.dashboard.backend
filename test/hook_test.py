from leancloud import Object, Query, init
import time

Installation = Object.extend('BindingInstallation')


def get_installationid_by_trackerid(tracker_id=None):
    print "tracker_id", tracker_id
    query = Query(Installation)
    user = {
        "__type": "Pointer",
        "className": "_User",
        "objectId": tracker_id
    }
    query.equal_to('user', user)
    query.descending('updatedAt')
    for i in query.find():
        print i.attributes
    print "query.count", query.count()
    installation = query.find()[0] if query.count() else {}
    # try:
    #     installation = query.first() or {}
    # except LeanCloudError:
    #     installation = {}
    print "query Installaton", installation
    print "query Installaton", installation.id
    return installation.id, installation.get('deviceType')

if __name__ == '__main__':
    init('2x27tso41inyau4rkgdqts0mrao1n6rq1wfd6644vdrz2qfo',
         '3fuabth1ar3sott9sgxy4sf8uq31c9x8bykugv3zh7eam5ll')

    print get_installationid_by_trackerid("568cd96160b2a09924491657")
