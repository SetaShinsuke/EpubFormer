# -*- coding: utf-8 -*-
PROXY_SERVER = '192.168.50.96:8787'
# RESIZE_SCALE = 0.9
RESIZE_SCALE = 1
REZIP_CONFIG = {
    # 画质 0-100
    'quality': 85,
    # scale = 1 也转换
    'force_convert': True,
    # webp, png
    'convert_webp': True,
    'convert_png': True
}
EPUB_CONFIG = {
    'fix_x': False # 修复文件名带有 [x] 的文件（已经处理过一遍的文件）
}
# REZIP_MODE = 'webp2jpg'
