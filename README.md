Hi There [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/R5R7L8YJ3)
# flickSnap: Reports for filmmakers

Hi! I made this tool so I can have some nice reports for my dailies. I hope you find it useful too :)

## Overview

The tool generates a report for a whole folder (the one that has all the video files, usually the copied video folder from camera) as a HTML file and if you want it can also do a PDF from the HTML, this is optional but I'll clarify that bellow. The script uses "gradio" as an UI so you'll have to copy and paste the IP address shown in terminal to your explorer, this is done locally so don't worry.

## How to use

The script asks for an **Input path** and the number of folders it has to go up so it can create a "Reports" folder there, the default value is 2 and minimum is 1, this is useful for me because normally I create a "Footage" folder in my project. The script will keep the original video folder name by creating a subfolder with the same name inside "Reports".

After a successful **Do HTML** run you can copy the **HTML Path** text from the webui and paste it to a new tab for review, then you could create a PDF with the **Do PDF** button if everything is correctly installed.

## Dependencies 

before you use this script you'll need to install: 
- **ffmpeg**  as an environment variable if you are on windows (you should be able to use it on terminal)
- **ghostscript** for the PDF feature. You can download it [here](https://www.ghostscript.com/)

If you use a mac I think both could be installed with [brew](https://brew.sh/index_es) but **I haven't try** if ghostcript works, ffmpeg worked as expected.

## Installation

You'll need Python 3.10, probably earlier versions should work too.
If you are on **windows** and don't care about "virtual environments" just run flickSnap.bat
If you want to have a "virtual environment" for this script for some reason just edit the bat file and delete the SKIP_VENV value, in this way it will create a VENV and activate it for the script.

Finally I you are on a **mac** or **linux** system just run "launch.py" from your terminal. If for some reason it gives you any problem try installing all the requirements from "requirements.txt" via "pip install ..."  and then run "main.py".

## Why gradio UI

Why not :P
