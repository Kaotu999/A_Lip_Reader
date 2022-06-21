from cv2 import VideoWriter
import face_recognition
import cv2

def crop(image):
    face_landmarks_list = face_recognition.face_landmarks(image)
    if face_landmarks_list != []:
        ws = []
        hs = []
        for (k, v) in face_landmarks_list[0]['top_lip'] + face_landmarks_list[0]['bottom_lip']:
            ws.append(k)
            hs.append(v)
        [x, y, w, h] = [min(ws), min(hs), max(ws), max(hs)]
        image = image[y:h, x:w]
    return image

class Vid():
    def __init__(self, file):
        self.cap = cv2.VideoCapture(file.name)
        self.cap.open(file.name)
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
        if int(major_ver)  < 3 :
            fps = self.cap.get(cv2.cv.CV_CAP_PROP_FPS)
        else :
            fps = self.cap.get(cv2.CAP_PROP_FPS)

        self.frame_count = int(self.cap.get(cv2. CAP_PROP_FRAME_COUNT))
        self.fps = fps
        self.lenght = self.frame_count/fps
        self.SEQUENCE_LENGHT = 4
        self.timepersequence = self.SEQUENCE_LENGHT/self.fps
        self.frames = []
        self.frames_cropped = []
        self.prediction = {}
        self.phone_timestamp = []
        self.possible_words = []
        self.width = 0
        self.height = 0

    def crop(self, progress_bar):
        run = 0
        while True:
            _, frame = self.cap.read()
            if frame is None:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self.frames.append(frame)
            self.frames_cropped.append(cv2.resize((crop(frame)),(64,64)))
            run += 1
            progress_bar.progress(run/self.frame_count)
        self.cap.release()
    
    def create_subs(self):
        #divide subs to see
        duration = 0
        sub = ""
        subs = []
        for i in self.phone_timestamp:
            duration = duration + i["duration"]
            sub = sub + i["phone"] + " "
            if duration > 1.12:
                subs.append(sub)
                duration = 0
                sub = ""
        times = 1
        self.subbed_frames = []
        print(subs)
        font = cv2.FONT_HERSHEY_SIMPLEX
        for _frame in range(len(self.frames)):
            frame = self.frames[_frame]
            oneframetime = self.lenght/self.frame_count
            if (_frame+1)*oneframetime > 1.12*times:
                times += 1
            if len(subs) > times-1:
                frame = cv2.putText(frame, subs[times-1], (100,100), font, 3, (255, 255, 255))
            self.subbed_frames.append(frame)

    def create_vid(self):
        size = self.frames[0].shape[1], self.frames[0].shape[0]
        out = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*'DIVX'), self.fps, size)
        for img in self.frames:
            out.write(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        out.release()