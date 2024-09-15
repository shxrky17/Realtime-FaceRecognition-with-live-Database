import cv2
import os
import pickle
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials, db, storage

# Initialize Firebase
cred = credentials.Certificate("c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/faceattendancerealtime-4da6e-firebase-adminsdk-vn6hc-6d1b3a114f.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-4da6e-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-4da6e.appspot.com"
})
bucket = storage.bucket()

# Capture video from webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Load background image
background_path = 'c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/Reasources/background.png'
imgBackground = cv2.imread(background_path)

# Load mode images (UI elements)
foldermode = 'c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/Reasources/Modes'
modepathlist = os.listdir(foldermode)
imgModelist = []

for path in modepathlist:
    imgModelist.append(cv2.imread(os.path.join(foldermode, path)))

# Load face encodings
file = open('encodefile.p', 'rb')
encodelistknownwithids = pickle.load(file)
file.close()
encodelistknown, studentids = encodelistknownwithids

# Initialize variables
modtype = 0
counter = 0
id = -1
imgStudent = []

# Main loop for capturing frames and processing
while True:
    success, img = cap.read()

    if not success:
        break

    # Resize and convert image to RGB for face recognition
    imgs = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)

    # Detect face locations and encodings in the current frame
    facecurframe = face_recognition.face_locations(imgs)
    encodecurframe = face_recognition.face_encodings(imgs, facecurframe)

    # Overlay the webcam frame on the background image
    imgBackground[162:162 + 480, 55:55 + 640] = img

    # Overlay the current mode UI on the background image
    if len(imgModelist) > modtype:
        imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[modtype]

    # Check for face matches only if no match is found yet
    if counter == 0:
        if len(facecurframe) > 0:
            for encodeface, faceloc in zip(encodecurframe, facecurframe):
                matches = face_recognition.compare_faces(encodelistknown, encodeface)
                facedistance = face_recognition.face_distance(encodelistknown, encodeface)
                matchindex = np.argmin(facedistance)

                if matches[matchindex]:
                    id = studentids[matchindex]
                    counter = 1
                    modtype = 1

    if counter != 0:
        if counter == 1:
            # Retrieve student information from Firebase
            studentsInfor = db.reference(f'Students/{id}').get()

            # Increment the total attendance if the key exists
            if 'total_attendaancce' in studentsInfor:
                ref = db.reference(f'Students/{id}')
                studentsInfor['total_attendaancce'] += 1
                ref.child('total_attendaancce').set(studentsInfor['total_attendaancce'])

                # Download student's image from Firebase storage
                try:
                    blob = bucket.get_blob(f'c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/images/{id}.jpg')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)

                    # Place the student's image on the background
                    imgBackground[175:175 + imgStudent.shape[0], 909:909 + imgStudent.shape[1]] = imgStudent

                except Exception as e:
                    print(f"Error loading student image: {e}")

        # Display student's details on the screen
        if 'total_attendaancce' in studentsInfor:
            cv2.putText(imgBackground, str(studentsInfor['total_attendaancce']), (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
            
            cv2.putText(imgBackground, str(studentsInfor['major']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 2)
            cv2.putText(imgBackground, str(id), (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 2)
            cv2.putText(imgBackground, str(studentsInfor['standing']), (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 2)
            cv2.putText(imgBackground, str(studentsInfor['year']), (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 2)
            cv2.putText(imgBackground, str(studentsInfor['starting_year']), (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 2)

            # Center the student's name on the screen
            (w, h), _ = cv2.getTextSize(studentsInfor['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
            offset = (414 - w) // 2
            cv2.putText(imgBackground, str(studentsInfor['name']), (800 + offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

            counter += 1
        else:
            print("Key 'total_attendaancce' not found in student info.")

    # Display the final image
    cv2.imshow("Face Attendance", imgBackground)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
