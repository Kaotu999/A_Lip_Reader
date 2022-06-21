import streamlit as st
import numpy as np
import pandas as pd
import tempfile
import vidtoimage
import classify
import os

def main():
    st.set_page_config(layout="wide")
    st.title("Lip Reader AI 💋")
    st.write("Upload your file\n- Please have your face and mouth clearly visible and try to exaggerate your lip motions.\n- The longer or higher resolution the video is, the longer it will take to process.\n- Subtitles are white on the to left corner of the video.\n- This may take a while so please be patient 😊")
    video_file = st.file_uploader("Upload You Video", type=['mp4','mov','wmv'])
    if video_file != None:
        if st.button("Process"):
            column = st.columns((1,1))
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(video_file.read())
            video = vidtoimage.Vid(tfile)
            with column[0]:
                #Video data
                expander = st.expander("Your Video Data", expanded=True)
                with expander:
                    st.markdown(f"fps: {video.fps}")
                    st.markdown(f"frames: {video.frame_count}")
                    st.markdown(f"lenght: {video.lenght} seconds")
                    st.markdown(f"Time per sequence: {video.timepersequence}")
                ###
            with column[1]:
                my_bar = st.progress(0)
            video.crop(my_bar)
            with column[1]:
                st.markdown("Now you know you might need to brush your teeth more often...")
                st.image(video.frames_cropped[0], width=250)
            classify.predict(video)
            video.create_subs()
            with column[0]:
                st.markdown("Preview...")
                st.image(video.subbed_frames[video.frame_count//2], width=500)
            video.create_vid()
            with open('output.mp4', 'rb') as f:
                st.download_button('Download video', f, file_name="output.mp4")
            os.remove("output.mp4")

if __name__ =="__main__":
    main()
