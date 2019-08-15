from app import db
from models import Tweets

db.create_all()

db.session.add(Tweets(
    "neiltyson",
    1161318161423228928,
    "What happens when you don’t pay close enough attention to the lyrics of #BohemianRhapsody... https://t.co/MEII14bbsX",
    "What happens when you don t pay close enough attention to the lyrics of BohemianRhapsody",
    109943622844380451,
    "23-Feb-2019 (22:30:00.000000)",
    13733,
    2265,
    116,
    0.0,
    0.5,
    "2019-02-23",
    "Saturday",
    22
))

db.session.commit()