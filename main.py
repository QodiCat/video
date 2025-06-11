import yaml
from utils.video_processor import process_videos

def load_config():
    """加载配置文件"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return None

def main():
    # 加载配置
    config = load_config()
    if not config:
        return
    
    # 处理视频
    process_videos(config)

if __name__ == "__main__":
    main()
