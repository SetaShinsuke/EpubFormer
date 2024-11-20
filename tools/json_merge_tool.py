import json
import os.path
import shutil
import sys
import re
from datetime import datetime

VOL_HEADS = "vol_heads"
VOL_NO = "vol_no"
CONFIG_KEY = "config"
BOOK_NAME = "book_name"


class JsonMergeTool:
    def __init__(self, _files_abs, _output_folder):
        self.files = _files_abs
        self.output_folder = _output_folder

    def merge(self):
        print("开始合并...")
        # 先分组:
        # {"vol_1": [task_001.json, task_002.json...], "vol_2": [] ...}
        groups = {}
        vol_heads = []
        # 找到卷首 index
        for file in self.files:
            # _vol_heads_xxx.json
            if re.search(VOL_HEADS, os.path.basename(file)):
                try:
                    # 复制一份到输出文件夹
                    shutil.copy(file, self.output_folder)
                    # 读取 vol_heads 文件
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
                groups[f'_vol_{datetime.now().microsecond}[unknown]'] = self.files
                break
            file_name = os.path.basename(file)
            chp_index = int(re.search('.*tasks_([\d]+).*.json', file_name)[1])
            vol_no = self.cal_vol_no(chp_index, vol_heads)["vol_name"]
            if vol_no not in groups:
                groups[vol_no] = []
            groups[vol_no].append(file)

        print("已分组，正在合并中...")
        i = 0
        # 根据 groups 整理 json
        for vol_no in groups:
            i += 1
            print(f'第 {i}/{len(groups)} 组合并中')
            config = None
            merged_json = {CONFIG_KEY: {}}  # 保证 config 在最前面
            files = groups[vol_no]
            for file in files:
                try:
                    raw_str = open(file, 'r', encoding='utf-8').read()
                    task_json = json.loads(raw_str)
                    # 初始化 config 字段
                    if (not config and CONFIG_KEY in task_json):
                        config = task_json[CONFIG_KEY]
                        if len(vol_heads) > 0:
                            config[VOL_HEADS] = vol_heads
                            config[VOL_NO] = vol_no.split('[')[0]
                        merged_json[CONFIG_KEY] = config
                        # del task_json[CONFIG_KEY]
                    for k in task_json:
                        if k == CONFIG_KEY:  # 防止 config 覆盖
                            continue
                        merged_json[k] = task_json[k]
                except Exception as e:
                    print("读取任务文件失败!")
                    print(e)
                    input("按任意键退出")
                    sys.exit(0)
            book_name = "unknown_book_"
            if BOOK_NAME in config:
                book_name = config[BOOK_NAME]
            merged_file = os.path.join(self.output_folder, f'tasks_{book_name}_Vol{vol_no}.json')
            print(f'合并完成, 准备保存: {merged_file}')
            with open(merged_file, 'w', encoding='utf8') as outfile:
                try:
                    json.dump(merged_json, outfile, ensure_ascii=False)
                    print(f'保存完成!')
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
            if (_chpIndex >= head):
                vol += 1
                start = head
                if _volHeads.index(start) + 1 < len(_volHeads):
                    end = _volHeads[_volHeads.index(start) + 1]
                    end -= 1
                else:
                    end = 'end'
        start = f'{start}'.rjust(3, '0')
        end = f'{end}'.rjust(3, '0')
        name = f'{vol}'.rjust(3, '0') + f'[{start}-{end}]'
        return {"vol_no": vol, "vol_name": f'{name}'}
