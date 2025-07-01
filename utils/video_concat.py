import os
import subprocess
from pathlib import Path

def concatenate_videos(video1_path, video2_path, output_path, temp_dir="temp"):
    """
    拼接两个视频文件
    
    Args:
        video1_path (str): 第一个视频文件路径
        video2_path (str): 第二个视频文件路径  
        output_path (str): 输出视频路径
        temp_dir (str): 临时文件目录
    """
    
    # 确保输出目录存在
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建临时目录
    temp_path = Path(temp_dir)
    temp_path.mkdir(exist_ok=True)
    
    try:
        # 方法1: 使用filter_complex进行拼接（推荐，处理不同分辨率/编码格式）
        print("开始拼接视频...")
        subprocess.run([
            'ffmpeg', '-y',  # -y 覆盖输出文件
            '-i', str(video1_path),
            '-i', str(video2_path),
            '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]',
            '-map', '[outv]',
            '-map', '[outa]',
            '-c:v', 'libx264',  # 视频编码
            '-c:a', 'aac',      # 音频编码
            '-preset', 'medium', # 编码速度/质量平衡
            str(output_path)
        ], check=True)
        
        print(f"视频拼接成功: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"拼接失败，尝试使用文件列表方法...")
        
        # 方法2: 使用文件列表进行拼接（适用于相同格式的文件）
        try:
            # 创建文件列表
            filelist_path = temp_path / "filelist.txt"
            with open(filelist_path, 'w', encoding='utf-8') as f:
                f.write(f"file '{Path(video1_path).absolute()}'\n")
                f.write(f"file '{Path(video2_path).absolute()}'\n")
            
            subprocess.run([
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(filelist_path),
                '-c', 'copy',  # 不重新编码，直接复制
                str(output_path)
            ], check=True)
            
            print(f"视频拼接成功: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e2:
            print(f"视频拼接失败: {str(e2)}")
            return False
        finally:
            # 清理临时文件
            if filelist_path.exists():
                filelist_path.unlink()
    
    finally:
        # 清理临时目录（如果为空）
        try:
            temp_path.rmdir()
        except OSError:
            pass  # 目录不为空或有其他文件

def concatenate_multiple_videos(video_paths, output_path, temp_dir="temp"):
    """
    拼接多个视频文件
    
    Args:
        video_paths (list): 视频文件路径列表
        output_path (str): 输出视频路径
        temp_dir (str): 临时文件目录
    """
    
    if len(video_paths) < 2:
        print("至少需要两个视频文件进行拼接")
        return False
    
    # 确保输出目录存在
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建临时目录
    temp_path = Path(temp_dir)
    temp_path.mkdir(exist_ok=True)
    
    try:
        # 创建文件列表
        filelist_path = temp_path / "filelist.txt"
        with open(filelist_path, 'w', encoding='utf-8') as f:
            for video_path in video_paths:
                if Path(video_path).exists():
                    f.write(f"file '{Path(video_path).absolute()}'\n")
                else:
                    print(f"警告: 文件不存在 {video_path}")
        
        print(f"开始拼接 {len(video_paths)} 个视频文件...")
        
        # 使用concat demuxer进行拼接
        subprocess.run([
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(filelist_path),
            '-c', 'copy',
            str(output_path)
        ], check=True)
        
        print(f"多个视频拼接成功: {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"多个视频拼接失败: {str(e)}")
        
        # 如果失败，尝试重新编码
        try:
            print("尝试重新编码拼接...")
            
            # 构建filter_complex参数
            inputs = []
            filter_parts = []
            
            for i, video_path in enumerate(video_paths):
                inputs.extend(['-i', str(video_path)])
                filter_parts.append(f'[{i}:v][{i}:a]')
            
            filter_complex = ''.join(filter_parts) + f'concat=n={len(video_paths)}:v=1:a=1[outv][outa]'
            
            cmd = [
                'ffmpeg', '-y'
            ] + inputs + [
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
                str(output_path)
            ]
            
            subprocess.run(cmd, check=True)
            print(f"重新编码拼接成功: {output_path}")
            return True
            
        except subprocess.CalledProcessError as e2:
            print(f"重新编码拼接也失败: {str(e2)}")
            return False
    
    finally:
        # 清理临时文件
        if 'filelist_path' in locals() and filelist_path.exists():
            filelist_path.unlink()
        
        # 清理临时目录（如果为空）
        try:
            temp_path.rmdir()
        except OSError:
            pass

def get_video_info(video_path):
    """获取视频信息"""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ], capture_output=True, text=True, check=True)
        
        import json
        info = json.loads(result.stdout)
        
        # 提取视频流信息
        video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
        audio_stream = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
        
        return {
            'duration': float(info['format']['duration']),
            'size': int(info['format']['size']),
            'video': {
                'codec': video_stream['codec_name'] if video_stream else None,
                'width': int(video_stream['width']) if video_stream else None,
                'height': int(video_stream['height']) if video_stream else None,
                'fps': eval(video_stream['r_frame_rate']) if video_stream else None
            },
            'audio': {
                'codec': audio_stream['codec_name'] if audio_stream else None,
                'sample_rate': int(audio_stream['sample_rate']) if audio_stream else None
            }
        }
    except Exception as e:
        print(f"获取视频信息失败 {video_path}: {str(e)}")
        return None

if __name__ == "__main__":
    # 示例用法
    video1 = "video1.mp4"
    video2 = "video2.mp4"
    output = "output/concatenated_video.mp4"
    
    # 拼接两个视频
    success = concatenate_videos(video1, video2, output)
    
    if success:
        print("视频拼接完成！")
    else:
        print("视频拼接失败！") 