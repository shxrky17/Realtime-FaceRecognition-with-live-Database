import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/faceattendancerealtime-4da6e-firebase-adminsdk-vn6hc-6d1b3a114f.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-4da6e-default-rtdb.firebaseio.com/"
    'storageBucket':"faceattendancerealtime-4da6e.appspot.com"
})




foldermode='c:/Users/chafl/OneDrive/Desktop/yash/FaceRecognition/images'
modepathlist=os.listdir(foldermode)
imglist=[]
studentids=[]
encodelist=[]
for path in modepathlist:
    imglist.append(cv2.imread(os.path.join(foldermode,path)))

    studentids.append(os.path.splitext(path)[0])
  
  
def findEncodings(imglist):
    for img in imglist:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB) 
        encode=face_recognition.face_encodings(img)[0]
        encodelist.append(encode)
    return encodelist

encodelistknown=findEncodings(imglist)   
encodelistknownwithids=[encodelistknown,studentids] 


file=open("encodefile.p",'wb')
pickle.dump(encodelistknownwithids,file)
file.close()
  