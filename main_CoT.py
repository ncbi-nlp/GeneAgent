import json
import time
import pandas as pd

import openai
## Replace with your own OpenAI model and key
openai.api_type = "azure"
openai.api_base = "***************"
openai.api_version = "*****************"
openai.api_key = "**************************" 

from worker import AgentPhD
from topic import topic_verification

if __name__ == "__main__":
    
    ## baseline 
    system = "You are an efficient and insightful assistant to a molecular biologist."
    task = lambda genes: f"Your task is to propose a biological process term for gene sets. Here is the gene set: {genes}"
    chain = f"""
    Let do the task step-by-step:
    Step1, write a cirtical analysis for gene functions. For each important point, discribe your reasoning and supporting information.
    Step2, analyze the functional associations among different genes from the critical analysis.
    Step3, summarize a brief name for the most significant biological process of gene set from the functional associations. 
    """
    instruction = """
    Put the name at the top of analysis as "Process: <name>" and follow the analysis.
    Be concise, do not use unnecessary words.
    Be specific, avoid overly general statements such as "the proteins are involved in various cellular processes".
    Be factual, do not editorialize.
    """
    
    data = pd.read_csv("Datasets/MsigDB/MsigDB.csv", header=0, index_col=None)
    for genes in data["Genes"]:
        genes = genes.replace(" ",",")
        ## send genes to GPT-4 and generate the original template of process name and analysis
        prompt_baseline = task(genes) + chain + instruction
        messages = [
            {"role":"system", "content":system},
            {"role":"user", "content":prompt_baseline}
        ]
        summary = openai.ChatCompletion.create(
			engine="gpt-4",
			messages=messages,
			temperature=0.0,
			)
        messages.append(summary.choices[0]["message"])
        summary = summary.choices[0]["message"]["content"]
        with open("Outputs/Chain-of-Thought/MsigDB_Response_CoT.txt","a") as f_update:
            f_update.write(summary+"\n")
            f_update.write("//\n")
        print("=====Summary=====")
        print(summary)
        
        
