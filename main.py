import epub_former
import sys
import os
from os.path import join

input_dir = join(os.getcwd(), 'input')
output_dir = join(os.getcwd(), 'output')

if(not os.path.exists(input_dir)):
    os.makedirs(input_dir)
if(not os.path.exists(output_dir)):
    os.makedirs(output_dir)

for index, file in enumerate(os.listdir(input_dir)):
    print(f'File.{index:02d}: {file}')
    file_path = join(input_dir, file)
    former = epub_former.EpubFormer(file_path, output_dir)
    former.start_forming()