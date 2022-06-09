import epub_former, zip_img_resizer
import sys
import os
from os.path import join
from Common.local_properties import RESIZE_SCALE

input_dir = join(os.getcwd(), 'input')
tmp_dir = join(os.getcwd(), 'tmp')
output_dir = join(os.getcwd(), 'output')

if (not os.path.exists(input_dir)):
    os.makedirs(input_dir)
if (not os.path.exists(tmp_dir)):
    os.makedirs(tmp_dir)
if (not os.path.exists(output_dir)):
    os.makedirs(output_dir)

i_epub = 0
i_zip = 0
for file in os.listdir(input_dir):
    if (file.endswith('.epub')):
        print(f'Epub File.{i_epub:02d}: {file}')
        i_epub += 1
        former = epub_former.EpubFormer(file, input_dir, tmp_dir, output_dir)
        former.start_forming()
    elif(file.endswith('.zip')):
        print(f'Zip File.{i_zip:02d}: {file}')
        i_zip += 1
        resizer = zip_img_resizer.ZipResizer(file, input_dir, tmp_dir, output_dir, RESIZE_SCALE)
        resizer.start_forming()
