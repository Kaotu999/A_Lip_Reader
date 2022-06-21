from msilib import sequence
import tensorflow as tf
from tensorflow import keras
import tensorflow.keras.models
import numpy as np

top = 2
classes = np.array(['aa', 'ae', 'ah', 'ao', 'aw', 'ay', 'b', 'ch', 'd', 'dh', 'eh',
       'er', 'ey', 'f', 'g', 'hh', 'ih', 'iy', 'jh', 'k', 'l', 'm', 'n',
       'ng', 'none', 'ow', 'oy', 'p', 'r', 's', 'sh', 't', 'th', 'uh',
       'uw', 'v', 'w', 'y', 'z', 'zh'], dtype='<U4')

pronunciations = {}
for line in open("cmudict-0.7b", 'r', errors='replace').readlines():
  line = line.strip()
  if line.startswith(";"): continue
  word, phones = line.split("  ")
  phones = phones.split(" ")
  for p in range(len(phones)):
    phones[p] = phones[p].replace("0", "")
    phones[p] = phones[p].replace("1", "")
    phones[p] = phones[p].replace("2", "")
    phones[p] = phones[p].lower()
  word = word.rstrip("(0123)").lower()
  if word not in pronunciations:
    pronunciations[word] = []
  pronunciations[word].append(phones)

model = keras.models.load_model("model_accuracy_35_loss_2.2/")

def predict(video):
    data = []
    for i in range(video.frame_count//video.SEQUENCE_LENGHT):
        sequence =[]
        for a in range(video.SEQUENCE_LENGHT):
            sequence.append(video.frames_cropped[i+a])
        data.append(np.array([sequence]))
    for _seq in range(len(data)):
        prediction = model.predict((data[_seq]))
        sort = np.sort(prediction[0])
        video.prediction[_seq] = (classes[np.where(prediction[0]==sort[-(top)])[0][0]])
    for _frames in range(len(video.prediction)):
        if len(video.phone_timestamp)!=0 and video.prediction[_frames] == video.phone_timestamp[-1]["phone"]:
            video.phone_timestamp[-1]["time_end"] = video.timepersequence*(_frames+1)
            video.phone_timestamp[-1]["duration"] = video.phone_timestamp[-1]["time_end"] - video.phone_timestamp[-1]["time_start"]
        else:
            pred = {}
            pred["phone"] = video.prediction[_frames]
            pred["time_start"] = video.timepersequence*_frames
            pred["time_end"] = video.timepersequence*(_frames+1)
            pred["duration"] = pred["time_end"] - pred["time_start"]
            video.phone_timestamp.append(pred)
    possible_words = [{"start_time":0}]
    word = []
    for _dict in range(len(video.phone_timestamp)):
        dict = video.phone_timestamp[_dict]
        if round(dict["duration"]) == round(video.timepersequence):
            word.append(dict["phone"])
        elif round(dict["duration"]) > round(video.timepersequence):
            word.append(dict["phone"])
            possible_words[-1]["time_end"] = video.phone_timestamp[_dict-1]["time_end"]
            possible_words[-1]["word"] = word
            possible_words.append({})
            possible_words[-1]["time_start"] = dict["time_start"]
            word = []
    words = []
    video.possible_words = possible_words

