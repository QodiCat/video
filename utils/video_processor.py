"""视频处理工具类
核心实现视频提取音频，生成字幕SRT和文本文件，并统计中文字符数量。

"""
import os
import subprocess
from pathlib import Path
import whisper
import json
import yaml

def load_config(config_path='config/video_processor.yaml'):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return None 
    
def count_chinese_chars(text):
    """统计中文字符数量"""
    return sum(1 for char in text if '\u4e00' <= char <= '\u9fff')

def ensure_directories(one_output_dir):
    """确保输出目录存在"""
    one_output_dir.mkdir(exist_ok=True)


def extract_audio(video_path, output_path):
    """从视频中提取音频"""
    try:
        subprocess.run([
            'ffmpeg', '-i', str(video_path),
            '-vn', '-acodec', 'libmp3lame',
            '-q:a', '2', str(output_path)
        ], check=True)
        print(f"成功提取音频: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"提取音频失败 {video_path}: {str(e)}")

def generate_subtitle(video_path, whisper_config,output_config):
    """使用whisper生成字幕"""
    
    model = whisper.load_model(whisper_config['model'])
    result = model.transcribe(str(video_path))
    output_dir=Path(output_config['output_dir'])
    one_output_dir=output_dir/video_path.stem
    if output_config['is_subtitle']:
        subtitle_path = one_output_dir /  f"subtitle.srt"
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], start=1):
                start = format_time(segment['start'])  # type: ignore
                end = format_time(segment['end'])      # type: ignore
                text = segment['text'].strip()         # type: ignore
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
    
    if output_config['is_text']:
        full_text = ""
        txt_path = one_output_dir / f"text.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], start=1):
                text = segment['text'].strip()         # type: ignore
                full_text += text + "，"
                f.write(f"{text}，")
        char_count = count_chinese_chars(full_text)
        print(f"文本总字数: {char_count}")
    
        json_path = one_output_dir / f"info.json"
        #将full_text和char_count写入json
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({'text': full_text, 'char_count': char_count}, f, ensure_ascii=False)
        
        
def format_time(seconds):
    """将秒数转换为SRT时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

def process_videos():
    """处理所有视频文件"""
    config = load_config()
    if not config:
        print("配置文件加载失败")
        return
    video_config=config['video']
    whisper_config=config['whisper']
    output_config=video_config['output']
    output_dir=Path(output_config['output_dir'])
    # 确保输出目录存在
    ensure_directories(output_dir)
    
    
    
    video_extensions = set(video_config['extensions'])

    video_files = [f for f in Path(video_config['input_dir']).glob("*") 
                  if f.suffix.lower() in video_extensions]
    
    for video_file in video_files:
        one_output_dir=Path(output_config['output_dir'])/video_file.stem
        ensure_directories(one_output_dir)
        if output_config['is_audio']:
            audio_path = one_output_dir / "audio.mp3"
            extract_audio(video_file,audio_path)
        generate_subtitle(video_file, whisper_config,output_config)
        

if __name__ == "__main__":
    # 这里需要传入config，或者从文件加载
    # process_videos()  # 需要config参数
    pass 