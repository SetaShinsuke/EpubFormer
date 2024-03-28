from os import makedirs
from os.path import join, dirname, exists, basename
import re
from PIL import Image, UnidentifiedImageError

from common.utils import flush, flush_reset


class WebpConvertTool:
    def __init__(self, _files_abs, _output_folder):
        self.files = _files_abs
        self.output_folder = _output_folder

    def covert2jpg(self, quality = 100):
        for f in self.files:
            file_name = re.sub(r'(.*).webp', r'\1.jpg', basename(f))
            result_path = join(self.output_folder, file_name)
            # 先创建文件夹
            makedirs(dirname(result_path), exist_ok=True)
            flush(f'result path: {result_path}')
            try:
                img = Image.open(f).convert('RGB')  # 保存
                img.save(result_path, quality=quality)
                flush(f'saved to {result_path}')
                img.close()
            except UnidentifiedImageError as e:
                # 不是图片文件
                flush_reset()
                print(f'Error reading image: {f}\nError: {e.args}')
        flush_reset()
