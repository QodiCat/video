import os
import subprocess
from pathlib import Path
import whisper

def count_chinese_chars(text):
    """统计中文字符数量"""
    return sum(1 for char in text if '\u4e00' <= char <= '\u9fff')

def ensure_directories(config):
    """确保输出目录存在"""
    if config['video']['is_audio']:
        Path(config['video']['output']['audio_dir']).mkdir(exist_ok=True)
    if config['video']['is_subtitle']:
        Path(config['video']['output']['subtitle_dir']).mkdir(exist_ok=True)

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

def generate_subtitle(video_path, output_path, config):
    """使用whisper生成字幕"""
    try:
        model = whisper.load_model(config['whisper']['model'])
        result = model.transcribe(str(video_path))
        
        # 保存为SRT格式，同时保存为txt
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], start=1):
                start = format_time(segment['start'])
                end = format_time(segment['end'])
                text = segment['text'].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{text}\n\n")
        
        #保存为txt
        full_text = ""
        txt_path = Path(config['video']['output']['subtitle_dir']) / f"{video_path.stem}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], start=1):
                text = segment['text'].strip()
                full_text += text + "，"
                f.write(f"{text}，")
        
        # 统计字数
        char_count = count_chinese_chars(full_text)
        print(f"文本总字数: {char_count}")
        
        print(f"成功生成字幕: {output_path}")
    except Exception as e:
        print(f"生成字幕失败 {video_path}: {str(e)}")

def format_time(seconds):
    """将秒数转换为SRT时间格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"

def process_videos(config):
    """处理所有视频文件"""
    ensure_directories(config)
    
    video_extensions = set(config['video']['extensions'])
    video_files = [f for f in Path(config['video']['input_dir']).glob("*") 
                  if f.suffix.lower() in video_extensions]
    
    for video_file in video_files:
        # 生成输出文件路径
        audio_path = Path(config['video']['output']['audio_dir']) / f"{video_file.stem}.mp3"
        subtitle_path = Path(config['video']['output']['subtitle_dir']) / f"{video_file.stem}.srt"
        
        
        extract_audio(video_file, audio_path)
        
        # 生成字幕
        generate_subtitle(video_file, subtitle_path, config)

if __name__ == "__main__":
    process_videos() 