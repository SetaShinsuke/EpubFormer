from os import makedirs
import os
import sys
from os.path import join, dirname, exists, basename
from pathlib import Path, PureWindowsPath
import re
from common.utils import flush, flush_reset


class TsConvertTool:
    def __init__(self, _files_abs, _output_folder):
        self.files = _files_abs
        self.output_folder = _output_folder

    def start_convert(self, format):
        for f_i in self.files:
            f = str(PureWindowsPath(f_i))
            print(f'Convert ts file {f} to mp4..., format: {format}')
            base_name = basename(f)
            print(f'basename: {base_name}')
            out_folder = self.output_folder
            if (out_folder == None):
                out_folder = dirname(f)
            file_name = re.sub(r'(.*).ts', r'\1.' + format, base_name)
            # file_name = re.sub(r' ', )
            result_path = PureWindowsPath(out_folder).joinpath(file_name)
            # 先创建文件夹
            makedirs(dirname(result_path), exist_ok=True)
            flush(f'result path: {result_path}')
            cmd = f'cmd /C "ffmpeg -i \"{f}\" -c copy \"{result_path}\""'
            print('\nCMD:')
            print(cmd)
            os.system(cmd)
            print(f'finish file: {result_path}')
