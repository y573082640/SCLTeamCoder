from experiment.baselines.glm import run_glm
from experiment.baselines.gpt import run_gpt
from experiment.baselines.qwen import run_qwen
from experiment.baselines.claude import run_claude
from experiment.baselines.llm4plc import run_llm4plc
from experiment.baselines.llama3 import run_llama3
from experiment.datasets.process import run_process
import torch as t    
print(t.cuda.is_available())  
print(t.__version__)

run_qwen(dataset="oscat_en")
