#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片转视频快速运行脚本
"""

from utils.images_to_video import main

if __name__ == "__main__":
    print("🎬 开始创建图片合成视频（双音轨）...")
    print("=" * 50)
    
    # 运行主程序
    exit_code = main()
    
    if exit_code == 0:
        print("=" * 50)
        print("🎉 视频创建完成！")
    else:
        print("=" * 50)
        print("❌ 视频创建失败！")
    
    input("\n按回车键退出...") 