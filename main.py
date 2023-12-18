from tools import epub_former, zip_img_resizer, json_merge_tool
import os
from os.path import join
from common.local_properties import RESIZE_SCALE, REZIP_CONFIG, EPUB_CONFIG

from tkinter import filedialog as fd
from pathlib import Path
from tkinter.messagebox import showinfo, askquestion

input_dir = join(os.getcwd(), 'input')
tmp_dir = join(os.getcwd(), 'tmp')
output_dir = join(os.getcwd(), 'output')

if (not os.path.exists(input_dir)):
    os.makedirs(input_dir)
if (not os.path.exists(tmp_dir)):
    os.makedirs(tmp_dir)
if (not os.path.exists(output_dir)):
    os.makedirs(output_dir)

# 系统默认下载目录
downloads_path = str(Path.home() / "Downloads")
print(f'Download dir: {downloads_path}')
filetypes = (
    ('JSON files', '*.json'),
    ('All files', '*.*'),
    ('Epub files', '*.epub'),
    ('Zip files', '*.zip')
)

selected_files = fd.askopenfilenames(
    title='选择文件',
    initialdir=downloads_path,
    filetypes=filetypes
)

# showinfo(
#     title='Selected File',
#     message=selected_files
# )

if not selected_files:
    use_input_dir = askquestion('提示', '未选择文件\n自动检查.\input目录?')
    # 不自动检测 input 目录
    if use_input_dir:
        selected_files = map(lambda file_name: join(input_dir, file_name), os.listdir(input_dir))
    else:
        selected_files = []

i_epub = 0
i_zip = 0
json_files = []
for file in selected_files:
    if (file.endswith('.epub')):
        print(f'Epub File.{i_epub:02d}: {file}')
        i_epub += 1
        former = epub_former.EpubFormer(file, tmp_dir, output_dir, EPUB_CONFIG)
        former.start_forming()
    elif (file.endswith('.zip')):
        print(f'Zip File.{i_zip:02d}: {file}')
        i_zip += 1
        resizer = zip_img_resizer.ZipResizer(file, tmp_dir, output_dir, RESIZE_SCALE, REZIP_CONFIG)
        print(f'Mode: {REZIP_CONFIG}')
        resizer.start_forming()
    elif file.endswith('.json'):
        json_files.append(file)

if len(json_files) > 0:
    merge_tool = json_merge_tool.JsonMergeTool(json_files, output_dir)
    merge_tool.merge()

print(f'任务结束!')

if (i_epub > 0 or i_zip > 0 or len(json_files) > 0) and askquestion('提示', '任务已完成\n是否打开输出文件夹?'):
    os.startfile(output_dir)
else:
    showinfo('提示', '任务已完成!')
