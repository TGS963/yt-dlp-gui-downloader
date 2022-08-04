# image_browser.py

import io
import PySimpleGUI as sg
import os
import sys
import requests
import json
import subprocess
import time
import threading
from PIL import Image, ImageTk

def Download(cmd, path):
    os.chdir(path)
    process = subprocess.Popen(cmd)
    process.wait()
    print("Download Finished")
    #sys.exit(0)

def main(link, path):
    code = ''
    if "shorts" in link:
        code = link[link.find("shorts")+7:]
    else:
        code = link[link.find("?v=")+3:]
    jpg_data = requests.get("https://i.ytimg.com/vi/"+code+"/maxresdefault.jpg").content        
    pil_image = Image.open(io.BytesIO(jpg_data))
    pil_image = pil_image.resize((480,270), resample=Image.Resampling.BICUBIC)
    png_bio = io.BytesIO()
    pil_image.save(png_bio, format="PNG")
    png_data = png_bio.getvalue()
    videoinfo = json.loads(os.popen("yt-dlp -j " + code).read())
    
    elements = [
        [
            sg.Image(data=png_data, key="thumbnail", size=(480,270)),
        ],
        [sg.Text(videoinfo['title'])],
        [sg.Text('Folder'), sg.In(default_text=path,size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse(initial_folder=path)],
        [
         sg.Button("Start"),
         sg.Button("Exit")
        ],
        [
            sg.Multiline("", size=(40, 9), autoscroll=True, reroute_stdout=True, reroute_stderr=True, key='-OUTPUT-')
        ],
    ]
    layout = [[sg.Column(elements, element_justification='c')]] 

    window = sg.Window("YouTube Downloader", layout, return_keyboard_events=True,)


    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Start":
            print("Download Started, Please do not click start again...")
            t = threading.Thread(target=Download,args=("yt-dlp --embed-subs --embed-metadata --progress --no-mtime --quiet " + code,values["-FOLDER-"],))
            t.start()

    window.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(0)
    else:
        main(sys.argv[1], sys.argv[2])
