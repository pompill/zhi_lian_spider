import pymongo


def parse():
    client = pymongo.MongoClient(host='localhost', port=27017)
    client.admin.authenticate("", "")
    db = client.fwwb
    city_name = db.zhilian_area
    data = city_name.find()
    return data