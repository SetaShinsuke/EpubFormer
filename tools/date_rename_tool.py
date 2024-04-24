import os, re
import time
from pathlib import Path
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo, askquestion

TIME_FORMAT = '%Y-%m-%d %H-%M-%S'

downloads_path = str(Path.home() / "Downloads")
print(f'Download dir: {downloads_path}')
filetypes = (
    ('All files', '*.*'),
    ('Mostly used', '.jpg .png .bmp .mp4 .avi')
)
selected_files = fd.askopenfilenames(
    title='选择要重命名的文件',
    initialdir=downloads_path,
    filetypes=filetypes
)

go_on = askquestion('提示', f'已选中{len(selected_files)}个文件\n是否开始重命名?')

if (go_on != 'yes'):
    showinfo('提示', '任务已取消!')
else:
    for f in selected_files:
        modified_at = os.path.getmtime(f)
        time_obj = time.strptime(time.ctime(modified_at))
        time_str = time.strftime(TIME_FORMAT, time_obj)
        # new_name = re.sub(r'(\.[^.]+)$', '_' + time_str + r'\1', f)
        old_name = os.path.basename(f)
        new_path = f.replace(old_name, f'{time_str}_{old_name}')
        print(f'Renaming: \n{f}\n{new_path}')
        # 重命名
        os.rename(f, new_path)

    showinfo('提示', '任务已完成!')
