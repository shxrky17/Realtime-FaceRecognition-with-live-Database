import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/faceattendancerealtime-4da6e-firebase-adminsdk-vn6hc-6d1b3a114f.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-4da6e-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-4da6e.appspot.com"
})

bucket = storage.bucket()

# Capture video from webcam
cap = cv2.VideoCapture(1)
cap.set(3, 640)
cap.set(4, 480)

# Load background and mode images
imgBackground = cv2.imread('c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/Reasources/background.png')
folderModePath = 'c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/Reasources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load face encodings
print("Loading Encode File ...")
try:
    with open('EncodeFile.p', 'rb') as file:
        encodeListKnownWithIds = pickle.load(file)
    encodeListKnown, studentIds = encodeListKnownWithIds
    print("Encode File Loaded")
except Exception as e:
    print(f"Error loading encode file: {e}")

modeType = 0
counter = 0
id = -1
imgStudent = []
show_duration = 30  # Duration to show student info mode (in frames)
display_counter = 0  # Counter to track display duration

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                counter = 1
                modeType = 1
                break  # Exit the loop after recognizing one face

    if counter != 0:
        if counter == 1:
            try:
                # Get student data
                studentInfo = db.reference(f'Students/{id}').get()
                if studentInfo:
                    print(studentInfo)
                    
                    # Get the student's image from storage
                    blob = bucket.get_blob(f'images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
                    
                    # Update attendance
                    last_attendance_time = datetime.strptime(studentInfo['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - last_attendance_time).total_seconds()
                    if secondsElapsed > 30:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            except Exception as e:
                print(f"Error processing student info or image: {e}")

        if modeType != 3:
            if display_counter <= show_duration:
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    if studentInfo:
                        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(id), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        if imgStudent is not None:
                            imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
                    else:
                        print("No student information available.")
                display_counter += 1

            if display_counter > show_duration:
                display_counter = 0
                modeType = 0
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    else:
        modeType = 0
        counter = 0
        display_counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
