#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
剔除视频中多余的音轨，只保留第一条音轨

用法:
    python remove_extra_audio.py            # 弹出文件浏览器，可多选文件
    python remove_extra_audio.py file1 file2 ...   # 命令行直接指定文件
"""

import os
import sys
import json
import shutil
import subprocess
import argparse


# ------------------------- 基础工具 -------------------------

def check_ffmpeg():
    """检查 ffmpeg / ffprobe 是否可用"""
    missing = [t for t in ("ffmpeg", "ffprobe") if shutil.which(t) is None]
    if missing:
        print(f"错误：未找到 {', '.join(missing)}，请先安装并加入 PATH")
        sys.exit(1)


def get_audio_streams(input_file):
    """使用 ffprobe 获取视频中所有音频流信息"""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a",
        "-show_entries",
        "stream=index,codec_name,channels,bit_rate:stream_tags=language,title",
        "-of", "json",
        input_file,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"  ffprobe 执行失败: {e.stderr.strip()}")
        return []
    try:
        return json.loads(result.stdout).get("streams", [])
    except json.JSONDecodeError:
        return []


def describe_stream(stream, idx):
    """把音频流信息格式化成可读字符串"""
    codec = stream.get("codec_name", "?")
    ch = stream.get("channels", "?")
    tags = stream.get("tags", {}) or {}
    lang = tags.get("language", "")
    title = tags.get("title", "")
    extras = []
    if lang:
        extras.append(f"lang={lang}")
    if title:
        extras.append(f"title={title}")
    extra_str = f" ({', '.join(extras)})" if extras else ""
    return f"  #{idx}: {codec}, {ch}ch{extra_str}"


# ------------------------- 核心处理 -------------------------

def remove_extra_audio(input_file,
                       output_suffix="_single_audio",
                       overwrite=False):
    """剔除多余的音轨，只保留第一条音轨。返回 True 表示生成了新文件。"""
    if not os.path.isfile(input_file):
        print(f"跳过：文件不存在 -> {input_file}")
        return False

    audio_streams = get_audio_streams(input_file)
    if not audio_streams:
        print(f"跳过：未检测到音频流 -> {input_file}")
        return False

    print(f"检测到 {len(audio_streams)} 条音轨：")
    for i, s in enumerate(audio_streams):
        print(describe_stream(s, i))

    if len(audio_streams) == 1:
        print("跳过：只有一个音轨，无需处理")
        return False

    base, ext = os.path.splitext(input_file)
    output_file = f"{base}{output_suffix}{ext}"

    # 如果输出路径和输入路径相同（比如 suffix 为空），直接拒绝，避免覆盖源文件
    if os.path.abspath(output_file) == os.path.abspath(input_file):
        print("跳过：输出文件名与输入相同（suffix 不能为空）")
        return False

    if os.path.exists(output_file) and not overwrite:
        print(f"跳过：输出文件已存在 -> {output_file}")
        return False

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y" if overwrite else "-n",
        "-i", input_file,
        "-map", "0:v?",      # 所有视频流
        "-map", "0:a:0",     # 只保留第一条音频流
        "-map", "0:s?",      # 所有字幕流
        "-c", "copy",        # 流复制，不重新编码
        "-map_metadata", "0",
        output_file,
    ]

    print(f"执行: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"  ffmpeg 处理失败: {e}")
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except OSError:
                pass
        return False

    print(f"  ✔ 完成 -> {output_file}")
    return True


# ------------------------- 文件选择 -------------------------

VIDEO_EXTS = (
    ".mp4", ".mkv", ".mov", ".avi", ".flv",
    ".ts", ".m4v", ".webm", ".wmv", ".mpg", ".mpeg", ".m2ts",
)


def pick_files_with_dialog():
    """弹出 tkinter 文件浏览器，允许选择多个视频文件"""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except ImportError:
        print("错误：未安装 tkinter，无法弹出文件浏览器")
        print("请使用命令行参数指定文件，或安装 python3-tk")
        sys.exit(1)

    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 让对话框置顶显示
    root.attributes("-topmost", True)

    filetypes = [
        ("视频文件", " ".join(f"*{e}" for e in VIDEO_EXTS)),
        ("所有文件", "*.*"),
    ]

    files = filedialog.askopenfilenames(
        title="请选择要处理的视频文件（可多选）",
        filetypes=filetypes,
    )

    root.destroy()
    return list(files)


def ask_overwrite_if_exists():
    """询问用户：当输出文件已存在时怎么处理"""
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError:
        return False

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    answer = messagebox.askyesno(
        "输出文件已存在",
        "某些输出文件已存在，是否覆盖？\n\n选『否』则跳过这些文件。",
    )
    root.destroy()
    return answer


# ------------------------- 命令行入口 -------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="剔除视频中多余的音轨，只保留第一条音轨"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="输入视频文件（不指定则弹出文件浏览器）",
    )
    parser.add_argument(
        "-s", "--suffix",
        default="_single_audio",
        help="输出文件名后缀（默认: _single_audio）",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="覆盖已存在的输出文件（不询问）",
    )
    parser.add_argument(
        "-n", "--no-gui",
        action="store_true",
        help="强制不使用 GUI 询问（已存在文件时直接跳过）",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    check_ffmpeg()

    # 1) 决定要处理的文件列表
    if args.files:
        files = [f for f in args.files if os.path.isfile(f)]
        missing = [f for f in args.files if not os.path.isfile(f)]
        for m in missing:
            print(f"警告：文件不存在 -> {m}")
    else:
        print("请在弹出的对话框中选择视频文件...")
        files = pick_files_with_dialog()

    if not files:
        print("未选择任何文件，退出")
        return

    print(f"\n共选择 {len(files)} 个文件\n")

    # 2) 预先检查是否存在输出文件，若存在则询问是否覆盖
    overwrite = args.force
    if not overwrite and not args.no_gui:
        pre = []
        for f in files:
            base, ext = os.path.splitext(f)
            out = f"{base}{args.suffix}{ext}"
            if os.path.exists(out):
                pre.append(out)
        if pre:
            print(f"检测到 {len(pre)} 个输出文件已存在")
            overwrite = ask_overwrite_if_exists()

    # 3) 逐个处理
    success = 0
    skipped = 0
    failed = 0
    for i, f in enumerate(files, 1):
        print(f"[{i}/{len(files)}] 处理: {f}")
        try:
            ok = remove_extra_audio(
                f,
                output_suffix=args.suffix,
                overwrite=overwrite,
            )
            if ok:
                success += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  处理时发生异常: {e}")
            failed += 1
        print("-" * 60)

    # 4) 汇总
    print(f"\n处理完成：成功 {success} / 跳过 {skipped} / 失败 {failed} / 共 {len(files)}")
    if not args.no_gui and args.files == []:
        # 弹个提示框
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showinfo(
                "处理完成",
                f"成功 {success} 个\n跳过 {skipped} 个\n失败 {failed} 个",
            )
            root.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    main()