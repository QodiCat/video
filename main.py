import yaml
from utils.video_processor import process_videos
from utils.images_to_video import begin_images_to_video
from utils.merge_subtitle import begin_merge_subtitle
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
    
    actions = config.get('actions', {})
    if actions.get('images_to_video', False):
        begin_images_to_video()
    if actions.get('process_videos', False):
        process_videos()
    if actions.get('begin_merge_subtitle', False):
        begin_merge_subtitle()

if __name__ == "__main__":
    main()


