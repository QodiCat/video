import subprocess
from pathlib import Path
import sys

def merge_subtitle_to_video(video_path, subtitle_path, output_path):
    """将字幕合并到视频中"""
    try:
        # 检查输入文件是否存在
        if not Path(video_path).exists():
            print(f"错误：视频文件不存在 - {video_path}")
            return False
        if not Path(subtitle_path).exists():
            print(f"错误：字幕文件不存在 - {subtitle_path}")
            return False

        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 使用ffmpeg合并字幕
        subprocess.run([
            'ffmpeg', '-i', str(video_path),
            '-vf', f"subtitles={subtitle_path}:force_style='FontName=Microsoft YaHei,FontSize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=1'",
            '-c:a', 'copy',
            str(output_path)
        ], check=True)
        
        print(f"成功生成带字幕的视频: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"合并字幕失败: {str(e)}")
        return False
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False

def main():
    if len(sys.argv) != 4:
        print("使用方法: python merge_subtitle.py <视频文件路径> <字幕文件路径> <输出文件路径>")
        print("示例: python merge_subtitle.py input.mp4 subtitle.srt output.mp4")
        return

    video_path = sys.argv[1]
    subtitle_path = sys.argv[2]
    output_path = sys.argv[3]

    merge_subtitle_to_video(video_path, subtitle_path, output_path)

if __name__ == "__main__":
    main() 