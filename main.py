import gradio as gr
import ffmpeg
from dominate import document
from dominate.tags import *
import os
import sys
import math
import shutil
from pyhtml2pdf import converter
from dataclasses import dataclass
from datetime import timedelta
from config.definitions import ROOT_DIR

@dataclass
class videoInfo:
    fileType: str
    duration: float
    fileSize: float
    fps: float
    resolution: str
    codec: str
    profile: str
    color_space: str

# Functions
# F Check Input
def check_user_input(input):
    try:
        # Convert it into integer
        input = int(input)
        if(input < 1):
            input = 2
    except ValueError:
        # default
        print("Input is not an integer, default value is 2")
        input = 2
    return input

# F Create Dirs
def create_dirs(root_dir, new_dir):
    # Path
    full_path = os.path.join(root_dir, new_dir)
    # Create the directory
    try:
        os.makedirs(full_path, exist_ok = True)
        return full_path
    except OSError as error:
        print(error)
        print("Directory '%s' can not be created" % new_dir)
        sys.exit(1)

# F Get Information
def get_information(input_file):
    args = {"v": "error",
            "select_streams": "v:0",
            # "show_entries": "format=duration",
            }
    rawData = (
            ffmpeg
            .probe(input_file , **args)
          )
    streamData = rawData.get('streams')
    codec = streamData[0].get('codec_name', 'NO DATA')
    profile = streamData[0].get('profile', 'NO DATA')
    w = streamData[0].get('width', 'NO DATA')
    h = streamData[0].get('height', 'NO DATA')
    resolution = str(w) + "x" + str(h)
    color_space = streamData[0].get('color_space', 'NO DATA')
    fps = streamData[0].get('r_frame_rate', 'NO DATA')
    fps = fps.split("/")
    fps = float(fps[0])/float(fps[1])
    formatData = rawData.get('format')
    fileType = formatData.get('format_long_name', 'NO DATA')
    duration = formatData.get('duration', 'NO DATA')
    duration = float(duration)
    fileSize = formatData.get('size', 'NO DATA')
    fileSize = float(fileSize)/1000000
    return videoInfo(fileType,duration,fileSize,fps,resolution,codec,profile,color_space)

# F Generate Thumb
# todo: Condicionar el caso en que el clip es un MXF de Arri, para usar el CLI de ARRIRAW
def generate_thumbnail(in_filename, out_filename, time, width):
    try:
        (
            ffmpeg
            .input(in_filename, ss=time)
            .filter('scale', width, -1)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)

# F Create Reports
def create_reports(input_path: str, n_cds: str, progress=gr.Progress()):
    
    # Check Folder Exist
    if os.path.exists(input_path) == False :
        log = "Error, check if folder exists"
        return log

    # check cds input
    n_cds = check_user_input(n_cds)

    # Print Folder name
    print("Reporte para:", input_path)

    # Check PATHLIB as alternative
    # Directory naming Setup
    snaps_dir = "Snapshots"
    split_dir = os.path.split(input_path)
    tail_dir = split_dir[1]
    parent_dir = split_dir[0]
    for i in range (1,n_cds):
        parent_dir = os.path.dirname(parent_dir)
    report_dir = os.path.join(parent_dir,"Reports")

    # Create Dirs
    output_path = create_dirs(report_dir, tail_dir)

    # Generate HTML
    with document(title='Reporte') as doc:
        doc.head.add(link(rel='stylesheet', href='style.css'))
        ClipCount = 0
        _cont = div(id="container")
        _main = main(role="application", cls = "App")
        _hgroup1 = hgroup()
        _hgroup1.add(h1('Reporte de ' + input_path.split("/")[-1])) 
        _folders = section(cls="Folders")
        _foldersStills = section(cls="Folder Folder--stills")
        _folderHeader = header(h1(input_path))
        _mediaFiles = div(cls="Media-Files")
        # Iterate directory
        for path in progress.tqdm(os.listdir(input_path), desc="Loading..."):
            # check if current path is a file
            in_file = os.path.join(input_path, path)
            if os.path.isfile(in_file) and path.lower().endswith(('.mov', '.mp4', '.avi', '.mxf')):
                ClipCount += 1
                oname = os.path.splitext(path)[0]
                snaps_path = create_dirs(output_path, os.path.join(snaps_dir,oname))
                clipInfo = get_information(in_file)
                _sectionM = section(cls="Media")
                _hgroup2 = hgroup()
                _hgroup2.add(h1(oname,cls="Media-Filename"))
                _hgroup2.add(h2("Metadata",cls="Media-CreatedAt"))
                _sectionM.add(header(_hgroup2))
                _mediaMeta=div(cls="Media-Metadata")
                _list1 = ol()
                _list1 += li(clipInfo.fileType)
                durConv = str(timedelta(seconds=clipInfo.duration)).split(':')
                durConv = durConv[0] + "h " + durConv[1] + "m " + "{:0.2f}".format(float(durConv[2])) + "s"
                _list1 += li(durConv)
                _list1 += li("{:0.2f}".format(clipInfo.fileSize)," MB")
                _mediaMeta.add(_list1)
                _list2 = ol()
                _list2 += li(clipInfo.resolution)
                _list2 += li(clipInfo.codec, " p:", clipInfo.profile)
                _list2 += li(clipInfo.fps," FPS")
                _mediaMeta.add(_list2)
                _list3 = ol()
                _list3 += li("color space ",clipInfo.color_space)
                _mediaMeta.add(_list3)
                _sectionM.add(_mediaMeta)
                _mediaStills=div(cls="Media-Stills")
                for i in range(3):
                    out_file = os.path.join(snaps_path, str(i)+".jpg")
                    generate_thumbnail(in_file, out_file, math.floor(clipInfo.duration*(float(i)/2.0) - (float(i-1)/clipInfo.fps)), 1920)
                    styleStr = "background-image: url('" + snaps_dir + "/" + oname + "/" + str(i)+ ".jpg" + "');"
                    _mediaStills.add(div(div(cls="Image", style = styleStr), cls = "Thumbnail"))
                _sectionM.add(_mediaStills)
                _mediaFiles.add(_sectionM)
        _header = header(_hgroup1,cls="Header")
        _header += div(ol(li("No. clips en la carpeta: ", ClipCount, cls="ClipCount")),cls="Summary")
        _foldersStills.add(_folderHeader)
        _foldersStills.add(_mediaFiles)
        _folders.add(_foldersStills)
        _main.add(_header)
        _main.add(_folders)
        _cont.add(_main)

    # Print number of clips
    print(ClipCount, "clips encontrados")

    # Write HTML
    htmlpath = os.path.join(output_path, 'gallery_' + tail_dir + '.html')
    with open(htmlpath, 'w') as f:
        f.write(doc.render())
        f.close()

    # Copy Styles css
    shutil.copyfile(os.path.join(ROOT_DIR, 'css', 'style.css'), os.path.join(output_path,'style.css'))

    # End
    print("--Finished--")
    # status = "Thumbs created"
    # return htmlpath, status
    return htmlpath

# Save PDF
def print_Pdf_Html(htmlpath: str):
    pdfpath = os.path.splitext(htmlpath)[0] + '.pdf'
    path = htmlpath
    converter.convert(f'file:///{path}', pdfpath)
    #print('pdf done')

# Gradio Interface
def webui():
    with gr.Blocks() as demo:
        with gr.Row():
            i_pth = gr.Textbox(
                label="Input path",
                info="folder with video files",
                placeholder="use absolute path!!",
                )
            folder_cnt = gr.Textbox(
                label="# folders to go up",
                info="Reports folder location",
                value="2",
                )
        btn1 = gr.Button("Do HTML")
        #cstatus = gr.Label(label="Progressbar")
        html_pth = gr.Textbox(
            label="HTML Path",
            info="Path to the report file, copy and paste to a new tab",
            placeholder="output here",
            )
        btn2 = gr.Button("Do PDF")
        btn1.click(create_reports, inputs=[i_pth, folder_cnt], outputs=[html_pth])
        btn2.click(print_Pdf_Html, inputs=[html_pth], outputs=[])
    return demo
    
# Main Call
if __name__ == '__main__':
    # call report func
    webui().queue().launch()