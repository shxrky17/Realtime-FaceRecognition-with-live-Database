import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone

# Open webcam
cap = cv2.VideoCapture(1)  # Change to 0 if you want to use the default webcam
cap.set(3, 640)  # Set webcam width
cap.set(4, 480)  # Set webcam height

# Load the background image
background_path = 'c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/Reasources/background.png'
imgBackground = cv2.imread(background_path)

# Load modes (images)
foldermode = 'c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/Reasources/Modes'
modepathlist = os.listdir(foldermode)
imgModelist = []

for path in modepathlist:
    imgModelist.append(cv2.imread(os.path.join(foldermode, path)))

# Load face encodings from file
file = open('encodefile.p', 'rb')
encodelistknownwithids = pickle.load(file)
file.close()
encodelistknown, studentids = encodelistknownwithids
print("Student IDs:", studentids)

while True:
    success, img = cap.read()
    
    if not success:
        print("Failed to capture webcam frame")
        break
    
    # Resize and convert to RGB for face recognition
    imgs = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)

    # Find all face locations and encodings in the current frame
    facecurframe = face_recognition.face_locations(imgs)
    encodecurframe = face_recognition.face_encodings(imgs, facecurframe)

    # Insert webcam image into the background at the specified location
    imgBackground[162:162 + 480, 55:55 + 640] = img  # Ensure dimensions match

    # Insert a mode image (like a side panel)
    if len(imgModelist) > 3:  # Make sure mode 3 exists
        imgBackground[44:44 + 633, 808:808 + 414] = imgModelist[3]

    # Process face recognition for detected faces
    for encodeface, faceloc in zip(encodecurframe, facecurframe):
        matches = face_recognition.compare_faces(encodelistknown, encodeface)
        facedistance = face_recognition.face_distance(encodelistknown, encodeface)
        
        print("Matches:", matches)
        print("Face Distance:", facedistance)

        # Find the best match
        matchindex = np.argmin(facedistance)
        if matches[matchindex]:
            print("Match found with index:", matchindex)
            student_id = studentids[matchindex]
            print("Student ID:", student_id)

            # Draw a bounding box around the face
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Scale back to original size
            bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)  # Offset for background placement
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

    # Show the combined result
    cv2.imshow("Face Attendance", imgBackground)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
