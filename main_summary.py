import json
import time
import pandas as pd
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

import openai
## Replace with your own OpenAI model and key
openai.api_type = "azure"
openai.api_base = "***************"
openai.api_version = "*****************"
openai.api_key = "**************************" 

from worker import AgentPhD

## baseline 
system = "You are an efficient and insightful assistant to a molecular biologist."
basewithoutfunctions = lambda genes: f"""
I will give you a list of human genes together with functional descriptions of some genes or gene set in all human genes.
Perform a term enrichment test on the human genes, i.e., tell me what the commonalities are in their function.
Make use of classification hierarchies when you do this.
Only report gene functions in common, not diseases. 
e.g if gene1 is involved in "toe bone growth" and gene2 is involved in "finger morphogenesis", then the term "digit development" would be enriched as represented by gene1 and gene2.
Only include terms that are statistically over-represented.
Also include a hypothesis of the underlying biological mechanism or pathway.
Here is the human gene set: {genes}
"""

base = lambda genes, functions: f"""
I will give you a list of genes together with their functional descriptions.  
Perform a term enrichment test on these genes. Also perform a Gene Ontology term tast on these genes.
i.e., tell me what the commonalities are in their function.
Make use of classification hierarchies when you do this.
Only report gene functions in common. 
e.g if gene1 is involved in "toe bone growth" and gene2 is involved in "finger morphogenesis", then the term "digit development" would be enriched as represented by gene1 and gene2.
Only include terms that are statistically over-represented.
Also include a hypothesis of the underlying biological mechanism, biological pathway or GO terms.
For each gene function, provide the corresponding genes.
Here is the human gene set:\n {genes}
Here is the gene functional descriptions:\n {functions}
"""


instruction = """
Provide results in the format

Summary: <high level summary>
Enriched Terms: <term1>; <term2>; <term3>
GO Terms: <term1>; <term2>; <term3>

For the list of terms, be sure to put each of them in a new line, and number the term.
Always put the list of terms last, after mechanism, summary, or hypotheses.
Don't use any unnecessary sentence as "As an AI..." or "I am sorry..."
"""

def extract_functions(text: str) -> list:
    segments = text.split('////')
    # Remove numbers and stop tokens ('-', '*')
    functions = []
    for ind in range(len(segments)):
        verify = []
        sentences = segments[int(ind)].split("&&\n")
        
        for claims in sentences[:-1]:
            if claims.startswith("\n[") or claims.startswith("["):
                continue
            
            else:    
                claim = claims.replace("\n\n","\n").split("\n")
                verification = "\n".join(claim[1:-1])
                verify.append(verification)
        functions.append(verify)

    return functions

def extract_synopsis(text: str) -> list:
    segments = text.split('////')
    # Remove numbers and stop tokens ('-', '*')
    functions = []
    for seg in segments:
        functions.append(seg)

    return functions


if __name__ == "__main__":
    
    data = pd.read_csv("Datasets/MsigDB/MsigDB.csv", header=0, index_col=None)
    genes = list(data["Genes"])
    print(len(genes))
    
    des = ""
    with open ("Verification Reports/Cascade/Claims_and_Verification_for_MsigDB.txt", "r") as gptfile:
        for line in gptfile.readlines():
            des += line
    functions = extract_functions(des)
    print(len(functions))
    
    assert len(genes) == len(functions)
        
    for gene, function in zip(genes, functions):
        gene = gene.replace(" ",",")

        ## send genes to GPT-4 and generate the original template of process name and analysis
        prompt = base(gene, function) + instruction
        messages = [
            {"role":"system", "content":system},
            {"role":"user", "content":prompt}
        ]
        summary = openai.ChatCompletion.create(
			engine="gpt-4-32k",
			messages=messages,
			temperature=0,
			)

        summary = summary.choices[0]["message"]["content"]
        with open("Outputs/EnrichedTermTest/gpt.geneagent.msigdb.summary.result.verification.txt","a") as f_summary:
            f_summary.write(summary+"\n")
            f_summary.write("//\n")
        print("=====Summary=====")
        print(summary)
        