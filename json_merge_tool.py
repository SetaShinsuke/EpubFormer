import json
import os.path
import sys
import re
from datetime import datetime

VOL_HEADS_FILE = "vol_heads"
CONFIG_KEY = "config"
BOOK_NAME = "book_name"


class JsonMergeTool:
    def __init__(self, _files_abs, _output_folder):
        self.files = _files_abs
        self.output_folder = _output_folder

    def merge(self):
        # 先分组:
        # {"vol_1": [task_001.json, task_002.json...], "vol_2": [] ...}
        groups = {}
        vol_heads = []
        # 找到卷首 index
        for file in self.files:
            # _vol_heads_xxx.json
            if re.search(VOL_HEADS_FILE, os.path.basename(file)):
                try:
                    raw_str = open(file, 'r', encoding='utf-8').read()
                    vol_heads = json.loads(raw_str)
                    self.files.remove(file)
                    # [1, 10, 12 ...]
                except Exception as e:
                    print("读取 vol_heads 文件失败!")
                    print(e)
                    input("按任意键退出")
                    sys.exit(0)
        # 根据 index 分组
        for file in self.files:
            if len(vol_heads) == 0:  # 没有分组信息，全部放到未知分卷里
                groups[f'_unknown_vol_{datetime.now().microsecond}'] = self.files
                pass
            file_name = os.path.basename(file)
            chp_index = int(re.search('.*tasks_([\d]+).*.json', file_name)[1])
            vol_no = self.cal_vol_no(chp_index, vol_heads)["vol_name"]
            if vol_no not in groups:
                groups[vol_no] = []
            groups[vol_no].append(file)

        # 根据 groups 整理 json
        for vol_no in groups:
            config = None
            merged_json = {}
            files = groups[vol_no]
            for file in files:
                try:
                    raw_str = open(file, 'r', encoding='utf-8').read()
                    task_json = json.loads(raw_str)
                    # 初始化 config 字段
                    if (not config and CONFIG_KEY in task_json):
                        config = task_json[CONFIG_KEY]
                        del task_json[CONFIG_KEY]
                    for k in task_json:
                        merged_json[k] = task_json[k]
                except Exception as e:
                    print("读取任务文件失败!")
                    print(e)
                    input("按任意键退出")
                    sys.exit(0)
            merged_json[CONFIG_KEY] = config
            book_name = "unknown_book_"
            if BOOK_NAME in config:
                book_name = config[BOOK_NAME]
            merged_file = os.path.join(self.output_folder, f'tasks_{book_name}{vol_no}.json')
            with open(merged_file, 'w', encoding='utf8') as outfile:
                try:
                    json.dump(merged_json, outfile, ensure_ascii=False)
                except BaseException as e:
                    print(f'Dump JSON error: {str(e)}')
                    print(e)
                    input("按任意键退出")
                    sys.exit(0)

    # 计算卷数
    def cal_vol_no(self, _chpIndex, _volHeads):
        vol = 0
        start = 'start'
        end = 'end'
        _volHeads.sort()
        for head in _volHeads:
            start = head
            if _volHeads.index(start) + 1 < len(_volHeads):
                end = _volHeads[_volHeads.index(start) + 1]
            if (_chpIndex >= head):
                vol += 1
            else:
                name = f'{vol}'.rjust(3, '0') + f'[{start}-{end}]'
                return {"vol_no": vol, "vol_name": f'{name}'}
