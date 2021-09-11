import zipfile
import os
from os.path import join
from Common.utils import clear_folder
import xml.etree.ElementTree as ET
import bs4


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
        # self.unzip()
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
        opf = None
        for f in os.listdir(self.tmp_folder):
            if (f.endswith('.opf')):
                opf = f
                break
        if (not opf):
            raise Exception('Opf file not found')
        tree = ET.parse(join(self.tmp_folder, opf))
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
            img_path = self.handleHtml(html_path, index)
            # todo: 修改 opf 和 图片文件

    # 读取 html 中的图片名, 并进行修改
    def handleHtml(self, html_path, img_index):
        with open(html_path, encoding='utf-8') as inf:
            txt = inf.read()
            soup = bs4.BeautifulSoup(txt, 'html.parser')
        src = soup.find('img')['src']
        img_path = os.path.normpath(join(html_path, '..', src.replace('/', '\\')))
        # 修改 src
        img_name = src.split('/')[-1]
        src = src.replace(img_name, f'{img_index:03d}_{img_name}')
        # todo: html 保存
        return img_path
