import os

# 动态获取项目根目录路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 定义数据目录路径
DATA_DIR = os.path.join(PROJECT_ROOT, 'rag_data/data')
RAG_DATA_DIR = os.path.join(PROJECT_ROOT, 'rag_data')
UTILS_DIR = os.path.join(PROJECT_ROOT, 'scl_team_coder/util')
EXPERIMENT_DIR = os.path.join(PROJECT_ROOT, 'experiment')

# 设置为你的api_key
GPT_API_KEY = os.getenv('GPT_API_KEY')
API_KEY_0520 = os.getenv('API_KEY_0520')
API_KEY_AIRX = os.getenv('API_KEY_AIRX')