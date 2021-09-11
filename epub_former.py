import zipfile
import os
from os.path import join
from Common.utils import clear_folder

class EpubFormer:

    def __init__(self, _file, _input_folder, _tmp_folder, _output_folder):
        self.file = _file
        self.file_full = join(_input_folder, _file)
        self.input_folder = _input_folder
        self.tmp_folder = _tmp_folder
        self.output_folder = _output_folder

    def start_forming(self):
        self.unzip()
        self.readOpf()
        pass

    def unzip(self):
        # 清空 tmp 工作目录
        print(f'Unzipping epub file...')
        clear_folder(self.tmp_folder)
        # 解压缩
        with zipfile.ZipFile(self.file_full, 'r') as zip_ref:
            zip_ref.extractall(self.tmp_folder)
        print(f'Unzipping finished')

    # [cover.html, 1.html, 2.html ...]
    def readOpf(self):
        pass
