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
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
    print("Download Finished")
    #sys.exit(0)

def main(link, path):
    videoinfo = json.loads(os.popen("yt-dlp -j " + link).read())
    
    videoresinfo = [] #Storing raw resolution info here
    rescode = [] #Storing video codes here
    resinfo = [] #Storing other info to show here
    for i in os.popen("yt-dlp -F " + link).read().splitlines():
        if "audio" not in i[:i.find('|')]:
            videoresinfo.append(i[:i.find('|')].split())
    for i in videoresinfo:
        badstrings = ['---','[','ID']
        if any(x in i[0] for x in badstrings) or 'mhtml' in i[1]:
            #print("bad value: ",i)
            continue
        try:
            resinfo.append(i[2] + " " + i[1] + " " + i[3] + "FPS")
        except:
            resinfo.append(i[2] + " " + i[1] + " ")
        rescode.append(i[0])

    jpg_data = requests.get(videoinfo['thumbnail']).content    
    pil_image = Image.open(io.BytesIO(jpg_data))
    pil_image = pil_image.resize((480,270), resample=Image.Resampling.BICUBIC)
    png_bio = io.BytesIO()
    pil_image.save(png_bio, format="PNG")
    png_data = png_bio.getvalue()
    sg.theme('Black')
    
    elements = [
        [
            sg.Image(data=png_data, key="thumbnail", size=(480,270)),
        ],
        [sg.Text(videoinfo['title'])],
        [sg.Text('Folder'), sg.In(default_text=path,size=(25,1), enable_events=True ,key='-FOLDER-'), sg.FolderBrowse(initial_folder=path)],
        [sg.Combo(resinfo, size=(25,1), default_value="Select Resolution", key='-LIST-')],
        [
         sg.Button("Video"),
         sg.Button("Audio Only"),
         sg.Button("Exit")
        ],
        [
            sg.Multiline("", size=(40, 9), autoscroll=True, reroute_stdout=True, reroute_stderr=True, key='-OUTPUT-')
        ],
    ]
    layout = [[sg.Column(elements, element_justification='c')]] 
    
    window = sg.Window("YouTube Downloader", layout, return_keyboard_events=True, icon='C:/Users/ghosh/OneDrive/Documents/progams/yt-dlp-gui-downloader/Papirus-Team-Papirus-Apps-Youtube.ico')

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Video":
            print("Download Started, Please do not click start again...")
            if (values['-LIST-'] == 'Select Resolution'):
                t = threading.Thread(target=Download,args=("yt-dlp --embed-subs --embed-metadata --progress --no-mtime -q " + link,values["-FOLDER-"],))    
            else:
                t = threading.Thread(target=Download,args=("yt-dlp -f " + rescode[resinfo.index(values['-LIST-'])] + "+bestaudio --embed-subs --embed-metadata --progress --no-mtime -q " + link,values["-FOLDER-"],))
            t.start()
        elif event == "Audio Only":
            print("Download Started, Please do not click start again...")
            t = threading.Thread(target=Download,args=("yt-dlp -f bestaudio --embed-subs --embed-metadata --progress --no-mtime -q " + link,values["-FOLDER-"],))    
            t.start()

    window.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(0)
    else:
        main(sys.argv[2], sys.argv[1])
