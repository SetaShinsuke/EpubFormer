import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# 音频码率：如果没读取到源码率则按此码率导出
AUDIO_BITRATE = "128k";
# 96, 128, 193, 256, 320


def check_ffmpeg():
    """检查系统是否安装了 ffmpeg / ffprobe"""
    for exe in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run(
                [exe, "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    return True


def get_audio_codec(input_path: str) -> str | None:
    """用 ffprobe 读取第一条音频流的编码名，如 'aac'；读不到则返回 None"""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name",
        "-of", "default=nw=1:nk=1",
        input_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    codec = result.stdout.strip().lower()
    return codec or None


def extract_audio_to_m4a(input_path: str) -> str:
    """
    从视频中提取音频并保存为 m4a。
    输出文件名与源文件同名，扩展名为 .m4a，保存在源文件所在目录。

    策略：
      - 源音频是 aac / alac：直接流复制，无损、瞬时完成。
      - 其他编码（ac3/dts/opus/vorbis 等）：转码为 AAC。
    """
    base, _ = os.path.splitext(input_path)
    output_path = base + ".m4a"

    codec = get_audio_codec(input_path)
    print(f"源音频编码: {codec}")

    cmd = ["ffmpeg", "-y", "-i", input_path, "-vn"]

    if codec in ("aac", "alac"):
        # 无损流复制，码率与源完全一致
        cmd += ["-c:a", "copy"]
    else:
        # 转为 AAC，质量档 2（约 190kbps VBR），音质与体积平衡
        # cmd += ["-c:a", "aac", "-q:a", "2"]
        # 固定码率
        cmd += ["-c:a", "aac", "-b:a", AUDIO_BITRATE]

    cmd.append(output_path)

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg 执行失败：\n{result.stderr[-1500:]}"
        )

    return output_path


def main():
    if not check_ffmpeg():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "缺少 ffmpeg",
            "未检测到 ffmpeg / ffprobe，请先安装并确保其在系统 PATH 中。\n\n"
            "Windows: https://ffmpeg.org/download.html 下载后将 bin 目录加入 PATH\n"
            "macOS:   brew install ffmpeg\n"
            "Linux:   sudo apt install ffmpeg",
        )
        return

    root = tk.Tk()
    root.withdraw()

    input_path = filedialog.askopenfilename(
        title="选择 MP4 视频文件",
        filetypes=[("MP4 视频", "*.mp4"), ("所有文件", "*.*")],
    )

    if not input_path:
        print("用户取消了选择。")
        return

    print(f"已选择: {input_path}")

    if not input_path.lower().endswith(".mp4"):
        messagebox.showwarning("提示", "所选文件不是 .mp4 文件，仍将尝试处理。")

    try:
        output_path = extract_audio_to_m4a(input_path)
        print(f"音频已提取: {output_path}")
        messagebox.showinfo("完成", f"音频已提取：\n{output_path}")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        messagebox.showerror("提取失败", str(e))


if __name__ == "__main__":
    main()