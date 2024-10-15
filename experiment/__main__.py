from experiment.baselines.glm import run_glm
from experiment.baselines.gpt import run_gpt
from experiment.baselines.qwen import run_qwen
from experiment.baselines.claude import run_claude
from experiment.baselines.llm4plc import run_llm4plc
from experiment.baselines.llama3 import run_llama3
from experiment.datasets.process import run_process

# run_gpt(dataset="lgf_en")
# run_glm(dataset="lgf_en")
# run_claude(dataset="lgf_en")
run_process()