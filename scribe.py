from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from splitter import Splitter
from tqdm import tqdm
import moviepy.editor as mp
import os
import sys
import io


class Scribe:
    '''
    Class meant to transcribe the audio to a data structure
    containing tuples of timestamps and respective strings captured
    from the video during the timestamp.
    '''
    def __init__(self, path, directory="audio_segments"):
        self.path = path
        self.directory = directory
        self.audio_file = os.path.splitext(self.path)[0] + ".mp3"
        self.audio_extracted = False
        self.segments = None
        self.papyrus = list()

    def split_by_silence(self):
        '''
        Uses the Splitter class to split the audio by silence
        to get the timestamps and respective filenames of the
        split segments.

        Segments is a list of tuples (filename, (start_time, end_time)).
        '''
        if(self.audio_extracted):
            splitter = Splitter(self.audio_file)
        else:
            raise Exception("ERROR: File has not been extracted from video yet.")

        splitter.run()
        self.segments = splitter.get_segments()

    def get_papyrus(self):
        return self.papyrus

    def extract_audio_from_video(self):
        '''
        Extract the audio from a video that has been
        passed as self.path.
        '''
        if(os.path.exists(self.audio_file)):
            print("Found file: " + str(self.audio_file))
            print("Audio already extracted... Skipping.")
            self.audio_extracted = True
            return

        clip = mp.VideoFileClip(self.path)
        clip.audio.write_audiofile(self.audio_file)
        self.audio_extracted = True

    def recognize(self, segment):
        '''
        Uses the Google Cloud API to recognize the given audio segment.
        Segment is a tuple ((start_time, end_time), filename).
        Runs long_running_recognize() if the audio segment is too long.
        '''
        client = speech_v1.SpeechClient()

        filename, timestamp = segment[0], segment[1]
        start, end = timestamp[0], timestamp[1]

        language_code = "en-US"
        sample_rate_hertz = 44100

        # We are using it on *.mp3 so we must use ENCODING_UNSPECIFIED
        encoding = enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED

        config = {
            "language_code": language_code,
            "sample_rate_hertz": sample_rate_hertz,
            "encoding": encoding,
            "enable_automatic_punctuation": True,
            "enable_word_time_offsets": True,
        }

        with io.open(filename, "rb") as f:
            content = f.read()
        audio = {"content": content}

        time_difference = int((end - start)/1000)

        if(time_difference < 60):
            response = client.recognize(config, audio)
        else:
            response = client.long_running_recognize(config, audio)

        transcripts = list()

        for result in response.results:
            # First alternative is the most probable result
            alternative = result.alternatives[0]
            transcripts.append(alternative.transcript)

        return (timestamp, transcripts)

    def scribble(self):
        '''
        Extracts audio from the provided *.mp4 file and then
        splits its audio by silence to get phrases that are mentioned.

        Afterwards, queries audio segments to the cloud API and returns
        it in a list of tuples ((start_time, end_time), list_of_strings)
        where start_time and end_time are in seconds.
        '''
        self.extract_audio_from_video()
        self.split_by_silence()

        if(self.segments == None):
            raise Exception("ERROR: Audio has not been split by silence.")

        print("Querying to Google Cloud API...")
        for segment in tqdm(self.segments):
            note = self.recognize(segment)
            self.papyrus.append(note)

    def peruse(self):
        '''
        Prints the papyrus data nicely to see exactly when each transcribed
        text was mentioned in the video
        '''
        for timestamp, transcripts in self.papyrus:
            start = timestamp[0]/1000
            end = timestamp[1]/1000
            print("Time:", start, end)
            for transcript in transcripts:
                print(transcript)


if(__name__ == '__main__'):
    path = sys.argv[1]
    scribe = Scribe(path)
    scribe.scribble()
    scribe.peruse()
