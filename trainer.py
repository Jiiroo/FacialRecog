import os
import cv2
import numpy as np
from PIL import Image

recognizer = cv2.face.LBPHFaceRecognizer_create()
path = 'references'
if not os.path.exists('./trainer'):
    os.makedirs('./trainer')


def get_image(paths):
    image_paths = [os.path.join(paths, f) for f in os.listdir(paths)]
    face = []
    ids = []
    for image_path in image_paths:
        face_img = Image.open(image_path).convert('L')
        face_np = np.array(face_img, 'uint8')
        id = int(os.path.split(image_path)[-1].split('.')[1])
        face.append(face_np)
        ids.append(id)
        cv2.waitKey(10)
    return np.array(ids), face


Ids, faces = get_image(path)
recognizer.train(faces, Ids)
recognizer.write('trainer/trainer.yml')
cv2.destroyAllWindows()
