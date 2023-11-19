from deepface import DeepFace
import matplotlib.pyplot as plt
import pytesseract
import cv2
import numpy as np
from PIL import Image
import pandas as pd
import os
from glob import glob

# haarcascade_frontalface_default.xml 얼굴인식 데이터셋 파일 사용에 따른 Intel License 의 copyright notice 의 게시.
"""
 Intel License Agreement
                For Open Source Computer Vision Library

 Copyright (C) 2000, Intel Corporation, all rights reserved.
 Third party copyrights are property of their respective owners.

 Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:

   * Redistribution's of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

   * Redistribution's in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.

   * The name of Intel Corporation may not be used to endorse or promote products
     derived from this software without specific prior written permission.

 This software is provided by the copyright holders and contributors "as is" and
 any express or implied warranties, including, but not limited to, the implied
 warranties of merchantability and fitness for a particular purpose are disclaimed.
 In no event shall the Intel Corporation or contributors be liable for any direct,
 indirect, incidental, special, exemplary, or consequential damages
 (including, but not limited to, procurement of substitute goods or services;
 loss of use, data, or profits; or business interruption) however caused
 and on any theory of liability, whether in contract, strict liability,
 or tort (including negligence or otherwise) arising in any way out of
 the use of this software, even if advised of the possibility of such damage.
"""


class faceDetect:
    def __init__(self, db):
        self.models = ["VGG-Face",
                       "Facenet",
                       "Facenet512",
                       "OpenFace",
                       "DeepFace",
                       "DeepID",
                       "ArcFace",
                       "Dlib",
                       "SFace", ]

        self.database = db

    def match_face(self, img1, img2=None, name=None):
        # precondition : img1에는 현재 사진데이터(or 경로), img2에는 민증사진데이터(or 경로), name에는 이름을 할당
        #                민증 사진을 주기 전에 생년월일로 성인인지 판별 후 성인일때만 함수 이용해야 한다.
        # postcondition: 민증 사진 없이 현재 사진만 입력하면 데이터베이스에 있는 사진들과 비교,
        #                두개 사진 모두 입력하면 2개의 사진 비교 일치하면 true 반환
        try:
            if isinstance(img1, str):
                img1 = cv2.imread(img1)

            if img2 == None:
                mustBeRemovedFile = self.database+"*.pkl"
                for f in glob(mustBeRemovedFile):
                    os.remove(f)
                
                dfs=pd.DataFrame()
                dfs = DeepFace.find(img_path=img1,
                                    db_path=self.database, model_name=self.models[2])
                print(dfs)
                if dfs.empty:
                    return False

                return True

            if isinstance(img2, str):
                img2 = cv2.imread(img2)

            result = DeepFace.verify(img1_path=img1, img2_path=img2, model_name=self.models[6])
            if result["verified"]:
                cv2.imwrite(self.database + "/" + name + "_pic" + ".jpg", img1)
                cv2.imwrite(self.database + "/" + name + "_ifm" + ".jpg", img2)
                return True

            return False

        except ValueError as v:
            # 얼굴 인식이 되지 않을때 예외 처리
            print(v)
            return False

    def show_face(self, img):
        # 이미지의 있는 얼굴들 출력
        try:
            faces = DeepFace.extract_faces(img, target_size=(224, 224), detector_backend="opencv")
            fig, axs = plt.subplots(int(len(faces) / 2 + 1), 2, figsize=(15, 10))
            axs = axs.flatten()

            for i, face in enumerate(faces):
                IMG = face["face"]
                axs[i].imshow(IMG)

            plt.show()

        except ValueError as v:
            print(v)

    def current_face(self):
        # 주환이형이 여기서 얼굴인식하고 인식했으면 그 값을 리턴해주세요

        # precondition : "captured.png" 사진 파일이 있어도 되고 없어도 된다. 이 기능의 목적은 사용자의 사진 촬영에 한한다.
        # postcondition: 3초 간의 얼굴 인식 후 촬영되면 "captured.png" 사진 파일이 생성 또는 갱신됨. (현재, 리턴 값은 없음)

        pictureTime = 3  # 사진촬영 대기 시간은 3초.

        camera = cv2.VideoCapture(0)  # 실행하는 장치의 카메라를 켜고 640 X 480 의 해상도로 설정한다.
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        faceRecognize = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        # 원활한 얼굴 인식을 위해 얼굴 인식 데이터 셋이 필요하기 때문에 Intel Corporation 의
        # haarcascade_frontalface_default.xml 파일을 사용하기로 하였다.

        while True:
            isCamera, captured = camera.read()  # 카메라로 captured 에 현재 영상 받아옴.
            grayCamera = cv2.cvtColor(captured, cv2.COLOR_BGR2GRAY)  # 카메라로 받아온 영상을 흑백영상으로 바꿈.

            recognizedFaces = faceRecognize.detectMultiScale(grayCamera, scaleFactor=1.01, minNeighbors=100,
                                                             minSize=(20, 20))
            # scaleFactor 를 1에 가깝게 하면 정확도가 오르지만 처리시간이 길어짐
            # minNeighbors 를 높이면 검출에 있어 좋아지지만 오탐지율도 상승함.

            captured = Image.fromarray(captured)  # 카메라로 촬영되는 영상을 송출할 수 있는 형태로 변환함.
            captured = np.array(captured)

            print(pictureTime)

            if len(recognizedFaces):  # 얼굴이 인식될 때 pictureTime 가 1씩 줄어들고 -1이 되면
                pictureTime -= 1  # Pictured! 문구와 함께 사각형이 빨간색으로 점등하며 사진이 저장된다.

                if pictureTime == -1:
                    cv2.imwrite('captured.png', captured)
                    for x, y, w, h in recognizedFaces:
                        cv2.rectangle(captured, (x, y), (x + w, y + h), (0, 0, 255), 2, cv2.LINE_4)
                    cv2.imshow("original", captured)
                    print("Pictured!")
                    cv2.waitKey(1000)
                    break

            if len(recognizedFaces):  # 얼굴을 인식하면 하얀색 사각형이 얼굴 주변에 위치한다.
                for x, y, w, h in recognizedFaces:
                    cv2.rectangle(captured, (x, y), (x + w, y + h), (255, 255, 255), 2, cv2.LINE_4)

            cv2.imshow("original", captured)  # 영상과 사각형이 합쳐진 형태가 송출된다.

            if cv2.waitKey(1000) == ord('q'):  # 1초마다 작업을 반복하고, 'q' 가 눌리는 경우 프로그램이 종료된다.
                break

        camera.release()
        cv2.destroyAllWindows()
        return captured
