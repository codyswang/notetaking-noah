from slidegrabber import Slidegrabber
from scribe import Scribe
import sys


class Patch:
    def __init__(self, timestamp, slide_path, script):
        # tuple with (slide_start, slide_end)
        self.timestamp = timestamp
        # path to slide (string)
        self.slide_path = slide_path
        # list of list of strings that were transcribed
        # and mentioned during the timestamp
        self.script = script

class Stitcher:
    def __init__(self, path):
        self.path = path
        self.quilt = list()

    def stitch(self):
        scribe = Scribe(self.path)
        slidegrabber = Slidegrabber(self.path)

        slides = slidegrabber.get_slides()
        scribe.scribble()
        scripts = scribe.get_papyrus()

        counter = 0

        print("Stitching timestamps together...")
        for slide_timestamp, slide_path in slides:

            slide_start, slide_end = slide_timestamp[0], slide_timestamp[1]

            script = list()

            while(counter < len(scripts) and scripts[counter][0][0] < slide_end):
                # append a list of strings
                script.append(scripts[counter][1])
                counter += 1

            timestamp = (slide_start, slide_end)
            self.quilt.append(Patch(timestamp, slide_path, script))

    def get_quilt(self):
        return self.quilt

if(__name__ == '__main__'):
    path = sys.argv[1]
    stitcher = Stitcher(path)
    stitcher.stitch()



