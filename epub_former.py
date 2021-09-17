import zipfile
import os
from os.path import join
import time
from Common.utils import clear_folder, flush, flush_reset
import xml.etree.ElementTree as ET
import bs4
import shutil

class EpubFormer:

    def __init__(self, _file, _input_folder, _tmp_folder, _output_folder):
        self.file = _file
        self.file_full = join(_input_folder, _file)
        self.input_folder = _input_folder
        self.tmp_folder = _tmp_folder
        self.output_folder = _output_folder
        self.pages = []

    def start_forming(self):
        # todo: 清空文件夹
        flush(f'Unzipping epub file [{self.file}]...')
        self.unzip()
        flush(f'Unzipping [{self.file}] fin')
        flush(f'Reading Opf')
        self.readOpf()
        flush(f'Reading Opf fin')
        flush(f'Zipping epub...')
        new_epub = self.zip_epub()
        flush(f'Zipping epub [{new_epub}] fin')
        flush_reset()

    def unzip(self):
        # 清空 tmp 工作目录
        clear_folder(self.tmp_folder)
        # 解压缩
        with zipfile.ZipFile(self.file_full, 'r') as zip_ref:
            zip_ref.extractall(self.tmp_folder)

    # [cover.html, 1.html, 2.html ...]
    def readOpf(self):
        opf = None
        for f in os.listdir(self.tmp_folder):
            if (f.endswith('.opf')):
                opf = f
                break
        if (not opf):
            raise Exception('Opf file not found')
        opf_path = join(self.tmp_folder, opf)
        tree = ET.parse(opf_path)
        root = tree.getroot()
        namespace = ''
        if (root.tag.startswith('{')):
            namespace = root.tag.split('}')[0] + '}'
        manifest = root.find(f'{namespace}manifest')
        spine = root.find(f'{namespace}spine')
        # spine → html → image
        # <itemref idref="Page_1" />
        for index, itemref in enumerate(spine):
            idref = itemref.attrib['idref']
            # <item id="Page_1" href="html/1.html" media-type="application/xhtml+xml"/>
            html_item = manifest.find(f"{namespace}item[@id='{idref}']")
            href = html_item.attrib['href'].replace('/', '\\')
            html_path = join(self.tmp_folder, href)
            flush(f'Handle html: [{html_path}]...')
            img_path, old_name, new_name = self.handleHtml(html_path, index)
            flush((f'Handle html: [{html_path}] fin!'))
            # todo: 修改 opf 和 图片文件
            # 重命名图片
            try:
                flush(f'Renaming img: {old_name} -> {new_name} ...')
                if(os.path.exists(img_path)):
                    os.rename(img_path, img_path.replace(old_name, new_name))
            except BaseException as e:
                flush_reset()
                print(f'Error when renaming: {e.args}')
            flush(f'Renaming[ {new_name} ] fin!')
            # 修改 manifest 中的文件名
            img_rel_path = img_path.replace(f'{self.tmp_folder}\\', '').replace('\\', '/')
            item_img = manifest.find(f"{namespace}item[@href='{img_rel_path}']")
            new_rel_path = img_rel_path.replace(old_name, new_name)
            flush(f'Editing OPF:[{img_rel_path}] -> [{new_rel_path}]...')
            item_img.set('href', new_rel_path)
            flush(f'Editing OPF:[{new_rel_path}] fin!')
        tree.write(opf_path)

    def handleHtml(self, html_path, img_index):
        '''
        读取 html 中的图片名, 并进行修改
        :param html_path: Html 文件的绝对路径
        :param img_index: 页码
        :return img_path, new_name: 图片的路径, 图片新文件名
        '''
        with open(html_path, encoding='utf-8') as inf:
            txt = inf.read()
            soup = bs4.BeautifulSoup(txt, 'html.parser')
        img = soup.find('img')
        src = img['src']
        img_path = os.path.normpath(join(html_path, '..', src.replace('/', '\\')))
        # 修改 src
        img_name = src.split('/')[-1]
        new_name = f'{img_index:03d}_{img_name}'
        img['src'] = src.replace(img_name, f'{img_index:03d}_{img_name}')
        # todo: html 保存
        flush(f'Editing html[{img_index}]...')
        with open(html_path, mode='wb') as f_output:
            f_output.write(soup.prettify('utf-8'))
        flush(f'Editing html[{img_index}] fin!')
        return img_path, img_name, new_name

    def zip_epub(self):
        try:
            zip_name = join(self.output_folder, self.file.split('.epub')[0].replace('.kepub', '').replace('[Mox.moe]',''))
            new_zip = shutil.make_archive(zip_name, 'zip', self.tmp_folder)
            new_epub = new_zip.replace('.zip', '.epub')
            flush(f'new file: {new_epub}')
            os.rename(new_zip, new_epub)
            return new_epub
        except BaseException as e:
            flush_reset()
            print(f'Error when zipping epub! {e.args}')