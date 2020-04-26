import os
import sys
import cv2
import numpy as np
from PIL import Image
import timeit
import glob

class Slidegrabber:
    def __init__(self, path, folder="slides"):
        self.path = path
        self.folder = folder
        try:
            os.mkdir(self.folder)
        except OSError:
            print ("Directory already created, skipping...")
        self.prev = folder + os.sep + "prev.jpg"
        self.cur = folder + os.sep + "cur.jpg"

    def get_percentage_difference(self, i1, i2):
        size = 128, 128
        i1 = Image.open(i1)
        i2 = Image.open(i2)
        i1.thumbnail(size)
        i2.thumbnail(size)
        pairs = zip(i1.getdata(), i2.getdata())
        if len(i1.getbands()) == 1:
            dif = sum(abs(p1-p2) for p1,p2 in pairs)
        else:
            dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
        ncomponents = i1.size[0] * i1.size[1] * 3
        percentage = (dif / 255.0 * 100) / ncomponents
        return percentage

    def remove_old_files(self):

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        os.chdir(self.folder)

        files=glob.glob('*.jpg')

        for filename in files:
            os.unlink(filename)

        os.chdir("..")

    def is_different(self):
        threshold = 1
        percentage = self.get_percentage_difference(self.prev, self.cur)
        if percentage > threshold:
            print("Difference exceeded threshold: " + str(percentage), end = ", ")
            return True
        else:
            return False

    def save(self, n):
        filename = self.folder + os.sep + os.path.basename(self.path) + str(n) + ".jpg"
        os.rename(self.prev, filename)
        print(str(n) + "th capture.")
        return filename

    def replace(self):
        try:
            os.remove(self.prev)
        except OSError:
            pass
        os.rename(self.cur, self.prev)

    def get_slides(self):
        slides = list()
        self.remove_old_files()

        cam = cv2.VideoCapture(self.path)
        fps = cam.get(cv2.CAP_PROP_FPS)
        n = 0
        count = 0
        a = cam.read()
        cv2.imwrite(self.prev, a[1])
        start = 0

        print("Grabbing slides...")
        while(True):
            ret,frame = cam.read()
            if ret:
                cv2.imwrite(self.cur, frame)
                if self.is_different():
                    filename = self.save(n)

                    end = count/fps
                    timestamp = (start, end)
                    start = end

                    slide = (timestamp, filename)
                    slides.append(slide)

                    n += 1
                self.replace()
                count += 30
                cam.set(1, count)
            else:
                break

        try:
            os.remove(self.prev)
            os.remove(self.cur)
        except OSError:
            pass

        cam.release()
        cv2.destroyAllWindows()

        return slides

if __name__ == '__main__':
    path = sys.argv[1]
    slidegrabber = Slidegrabber(path)
    slidegrabber.get_slides()
