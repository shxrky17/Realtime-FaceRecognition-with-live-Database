import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/faceattendancerealtime-4da6e-firebase-adminsdk-vn6hc-6d1b3a114f.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-4da6e-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendancerealtime-4da6e.appspot.com"
})



ref = db.reference('Students')

data = {
    "321654":
        {
            "name": "Murtaza Hassan",
            "major": "Robotics",
            "starting_year": 2017,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "852741":
        {
            "name": "Emly Blunt",
            "major": "Economics",
            "starting_year": 2021,
            "total_attendance": 12,
            "standing": "B",
            "year": 1,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "963852":
        {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2020,
            "total_attendance": 0,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
       
        "yash":
        {
            "name": "yash",
            "major": "computer science",
            "starting_year": 2020,
            "total_attendance": 1,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        },
         "69":
        {
            "name": "PUNNEEETT",
            "major": "LORD",
            "starting_year": 2020,
            "total_attendance": 0,
            "standing": "G",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
        }
        
}

for key, value in data.items():
    ref.child(key).set(value)