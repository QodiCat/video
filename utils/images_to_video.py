#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片序列转视频脚本 - 支持双音轨
"""

import os
import glob
from moviepy.editor import (
    ImageSequenceClip, 
    AudioFileClip, 
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_audioclips,
    concatenate_videoclips
)
import yaml


def load_config():
    """加载配置文件"""
    with open('config/images_to_video.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_sorted_images(images_dir):
    """获取排序后的图片列表"""
    # 支持的图片格式
    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
    
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(images_dir, ext)))
    
    # 按文件名数字排序 (0.png, 1.png, 2.png, 3.png)
    image_files.sort(key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
    
    return image_files


def get_audio_files(audio_dir):
    """获取音频文件列表"""
    audio_extensions = ['*.mp3', '*.wav', '*.aac', '*.m4a']
    
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(glob.glob(os.path.join(audio_dir, ext)))
    
    return audio_files


def create_video_with_dual_audio(images_dir="input_images", 
                                audio_dir="input_audio", 
                                output_path="output/combined_video.mp4",
                                duration_per_image=2.0,
                                fps=24,
                                audio_count=1
                                ):
    """
    创建带双音轨的视频
    
    Args:
        images_dir: 图片目录
        audio_dir: 音频目录  
        output_path: 输出视频路径
        duration_per_image: 每张图片显示时长（秒）
        fps: 视频帧率
    """
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 获取图片文件
    image_files = get_sorted_images(images_dir)
    if not image_files:
        raise ValueError(f"在 {images_dir} 中没有找到图片文件")
    
    print(f"找到 {len(image_files)} 张图片:")
    for img in image_files:
        print(f"  - {os.path.basename(img)}")
    
    # 获取音频文件
    audio_files = get_audio_files(audio_dir)
    if len(audio_files) < 1:
        raise ValueError(f"需要至少1个音频文件，但在 {audio_dir} 中只找到 {len(audio_files)} 个")
    
    print(f"找到 {len(audio_files)} 个音频文件:")
    for audio in audio_files:
        print(f"  - {os.path.basename(audio)}")
    
    # 创建图片序列视频
    print("\n正在创建图片序列视频...")
    video_duration = len(image_files) * duration_per_image
    # 为每张图片创建指定时长的片段
    clips = []
    for i, img_path in enumerate(image_files):
        clip = ImageSequenceClip([img_path], durations=[duration_per_image])
        clips.append(clip)
    
    # 连接所有图片片段
    video_clip = concatenate_videoclips(clips, method="compose")
    video_clip = video_clip.set_fps(fps)
    
    print(f"视频时长: {video_duration} 秒")
    
    # 处理音频轨道
    print("\n正在处理音频轨道...")
    audio_clips = []

    for audio_path in audio_files[:audio_count]:  # 只使用前audio_count个音频文件
        audio = AudioFileClip(audio_path)
        
        # 如果音频比视频长，截取到视频长度
        if audio.duration > video_duration:
            audio = audio.subclip(0, video_duration)
        # 如果音频比视频短，循环播放
        elif audio.duration < video_duration:
            loops_needed = int(video_duration / audio.duration) + 1
            audio = concatenate_audioclips([audio] * loops_needed).subclip(0, video_duration)
        
        audio_clips.append(audio)
        print(f"  - {os.path.basename(audio_path)}: {audio.duration:.2f}s")
    
    # 混合两个音轨
    print("\n正在混合音轨...")
    mixed_audio = CompositeAudioClip(audio_clips)
    
    # 将音频添加到视频
    final_video = video_clip.set_audio(mixed_audio)
    
    # 输出视频
    print(f"\n正在输出视频到: {output_path}")
    final_video.write_videofile(
        output_path,
        fps=fps,
        audio_codec='aac',
        codec='libx264',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )
    
    # 清理资源
    video_clip.close()
    mixed_audio.close()
    for clip in clips:
        clip.close()
    for audio in audio_clips:
        audio.close()
    
    print(f"\n✅ 视频创建完成: {output_path}")
    print(f"   - 图片数量: {len(image_files)}")
    print(f"   - 视频时长: {video_duration:.2f}秒")
    print(f"   - 音轨数量: {len(audio_clips)}")


def begin_images_to_video():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        
        # 获取输出目录配置
        output_config = config.get('video', {}).get('output', {})
        input_config = config.get('video', {}).get('input', {})

        # 设置输入路径
        images_dir = input_config.get('input_dir', 'input_images')
        audio_dir = input_config.get('audio_dir', 'input_audio')
        # 设置输出路径
        output_path = os.path.join(output_config.get('output_dir', 'output'), "combined_video.mp4")
        #设置视频帧率和每张图片显示时长
        duration_per_image = output_config.get('duration_per_image', 3.0)  
        fps = output_config.get('fps', 24)

        # 创建视频
        create_video_with_dual_audio(
            images_dir=images_dir,
            audio_dir=audio_dir,
            output_path=output_path,
            duration_per_image=duration_per_image,
            fps=fps,
            audio_count=output_config.get('audio_count', 1)
        )
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    return 0

