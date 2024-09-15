import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/faceattendancerealtime-4da6e-firebase-adminsdk-vn6hc-6d1b3a114f.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-4da6e-default-rtdb.firebaseio.com/"

})
ref=db.reference('Students')
data={
    "yash":{
        "name":"yash chafle",
        "major":"computer technology",
        "starting_year":"2022",
        "total_attendaancce":6,
        "standing":"F",
        "year":3,
        "last_attendance_time":"2024/9/15 22:38:14"
    },
    "vaishnavi":{
        "name":"vaishnavi jemati",
        "major":"computer technology",
        "starting_year":"2022",
        "total_attendaancce":6,
        "standing":"A",
        "year":3,
        "last_attendance_time":"2024/9/15 22:38:14"
    }
}

for key,value in data.items():
    ref.child(key).set(value)