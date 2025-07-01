import subprocess
from pathlib import Path
import sys
import yaml

def load_config():
    """加载配置文件"""
    try:
        with open('config/merge_subtitle.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return None 


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

def begin_merge_subtitle():
    """开始合并字幕到视频"""
    config = load_config()
    if not config:
        return

    input_config = config.get('input', {})
    output_config = config.get('output', {})

    video_path = input_config.get('video_path', 'input_video.mp4')
    subtitle_path = input_config.get('subtitle_path', 'input_subtitle.srt')
    output_path = output_config.get('output_path', 'output/merged_video.mp4')

    if not video_path or not subtitle_path or not output_path:
        print("配置文件中缺少必要的路径信息")
        return

    merge_subtitle_to_video(video_path, subtitle_path, output_path)

if __name__ == "__main__":
    begin_merge_subtitle()