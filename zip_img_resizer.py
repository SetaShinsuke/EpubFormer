# -*- coding: utf-8 -*-
from os import walk, rename, makedirs
from os.path import join, dirname
from Common.utils import clear_folder, flush, flush_reset
import zipfile
from PIL import Image, UnidentifiedImageError
import shutil


class ZipResizer:
    def __init__(self, _file, _input_folder, _tmp_folder, _output_folder, _scale):
        self.file = _file
        self.file_full = join(_input_folder, _file)
        # self.input_folder = _input_folder
        self.tmp_folder = _tmp_folder
        self.output_folder = _output_folder
        self.scale = _scale

    # 解开zip包，给每张图片缩放，再打包输出
    def start_forming(self):
        # 清空tmp文件夹
        clear_folder(self.tmp_folder)
        flush(f'Unzipping zip file: [{self.file}]')
        unzipFolder = self.unzip()
        flush(f'Unzipping zip file: [{self.file}] fin!')
        flush(f'Start resizing imgs...')
        # [第021话][第022话]...
        # for f in listdir(self.tmp_folder):
        #     # \tmp\第021话
        #     fPath = join(self.tmp_folder, f)
        #     if (isdir(f)):
        for root, dirs, files in walk(self.tmp_folder):
            for f in files:
                imgPath = join(root, f)
                imgResultPath = imgPath.replace(self.tmp_folder, self.output_folder)
                # 转换为 .jpg 格式
                if(imgResultPath.endswith('.png')):
                    imgResultPath = imgResultPath[:-4] + '' + '.jpg'
                # 先创建文件夹
                makedirs(dirname(imgResultPath), exist_ok=True)
                flush(f'result path: {imgResultPath}')
                # 调整大小
                try:
                    img = Image.open(imgPath)
                    width, height = img.size
                    img = img.resize((int(width * self.scale), int(height * self.scale)),
                                     Image.ANTIALIAS)
                    # img.show()
                    img.save(imgResultPath)
                    flush(f'saved to {imgResultPath}')
                except UnidentifiedImageError as e:
                    # 不是图片文件
                    flush_reset()
                    print(
                        f'Error reading image: {f}\nError: {e.args}\nJust copy file to target folder')
                    shutil.copy(imgPath, imgResultPath)
                # break
        flush_reset()
        # todo: 打包 zip
        # ...\output\漫画名[01-05]\
        toZipFolder = unzipFolder.replace(self.tmp_folder, self.output_folder)
        print(f'to zip: {toZipFolder}')
        shutil.make_archive(toZipFolder, 'zip', toZipFolder)

    def unzip(self):
        # 清空 tmp 工作目录
        clear_folder(self.tmp_folder)
        # 解压缩
        with zipfile.ZipFile(self.file_full, 'r') as zip_ref:
            # ...\tmp\火影忍者[X]
            dest = join(self.tmp_folder, self.file.replace('.zip', '[X]'))
            for f in zip_ref.namelist():
                # dest = join(dest, f)
                # print(dest)
                zip_ref.extract(f, dest)
                name = join(dest, f)
                try:
                    f.encode('gbk')
                    # 是gbk编码
                except BaseException:
                    try:
                        # 是cp437编码 ...\tmp\乱码*&(*&^
                        nameNew = join(dest, f.encode('cp437').decode('gbk'))
                        makedirs(dirname(nameNew), exist_ok=True)
                        rename(name, nameNew)
                    except BaseException as e:
                        print(f'Error Renaming file: {e.args}')
            return dest

# class ImgFile:
#     def __init__(self, ):
