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

logger = logging.getLogger('AgentLogger')
logger.setLevel(logging.INFO)

log_filename = 'logs.txt'
file_handler = RotatingFileHandler(log_filename, maxBytes=10000000, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

## baseline 
system = "You are an efficient and insightful assistant to a molecular biologist."
baseline = lambda genes: f"""
Write a critical analysis of the biological processes performed by this system of interacting proteins.
Propose a brief name for the most prominent biological process performed by the system. 
Put the name at the top of the analysis as "Process: <name>".
Be concise, do not use unnecessary words.
Be specific, avoid overly general statements such as "the proteins are involved in various cellular processes".
Be factual, do not editorialize.
For each important point, describe your reasoning and supporting information.
For each biological function name, show the corresponding gene names.
Here is the gene set: {genes}
"""

## GeneAgent
system_verify = "You are a helpful and objective fact-checker to verify the summary of gene set."
topic = lambda genes, process: f"""
Here is the original process name for the gene set {genes}:\n{process}
However, the process name might be false. Please generate decontextualized claims for the process name that need to be verified.
Please return JSON list only containing the generated strings of claims:
"""
topic_instruction = """
Only generate claims with affirmative sentence for the entire gene set.
Claims must contain a list of gene names corresponding their common function.
Don't generate claims for the single gene or incomplete gene set.
Don't generate hypotheis claims over the previous analysis like diseases, mutations, disruptions, etc.
"""

analysis = lambda genes, updated_summary: f"""
Here is the updated summary for the gene set {genes}: \n{updated_summary}
However, the gene analysis in the summary might not support the updated process name. Please generate decontextualized claims for the gene analysis that need to be verified.
Please return a JSON list only containing the generated strings of claims:
"""
analysis_instruction = """
Must generate claims for multiple genes in the similar biological function around the updated process name.
Don't generate claims for the entire gene set or 'this system'.
Don't generate unworthy claims such as the summarization and reasoning over the previous analysis. 
Don't generate hypotheis claims for genes like disease, mutations, disruptions, etc.
Claims must contain the gene names and their biological process functions.
"""

## For NeST and MsigDB
reposits = [
    "get_complex_ids_for_gene_set",
    "get_disease_id_for_single_gene",
    "get_domain_id_for_single_gene",
    "get_enrichment_for_gene_set",
    "get_pathway_for_gene_set",
    "get_complex_names_for_complex_ids",
    "get_disease_name_for_disease_id",
    "get_domain_name_for_domain_id",
    "get_interactions_for_gene_set",
    "get_gene_summary_for_single_gene",
    "get_pubmed_articles"
]

## For Gene Ontology
# reposits = [
#     "get_complex_ids_for_gene_set",
#     "get_disease_id_for_single_gene",
#     "get_domain_id_for_single_gene",
#     # "get_enrichment_for_gene_set",
#     "get_pathway_for_gene_set",
#     "get_complex_names_for_complex_ids",
#     "get_disease_name_for_disease_id",
#     "get_domain_name_for_domain_id",
#     "get_interactions_for_gene_set",
#     "get_gene_summary_for_single_gene",
#     "get_pubmed_articles"
# ]

agentphd = AgentPhD(function_names=reposits)

if __name__ == "__main__":
    
    data = pd.read_csv("Datasets/MsigDB/MsigDB.csv", header=0, index_col=None)
    for ID, genes in zip(data["ID"], data["Genes"]):
        genes = genes.replace(" ",",")

        ## send genes to GPT-4 and generate the original template of process name and analysis
        try:
            prompt_baseline = baseline(genes)
            messages = [
                {"role":"system", "content":system},
                {"role":"user", "content":prompt_baseline}
            ]
            summary = openai.ChatCompletion.create(
                engine="gpt-4-32k",
                messages=messages,
                temperature=0,
                )
            messages.append(summary.choices[0]["message"])
            summary = summary.choices[0]["message"]["content"]
            with open("Outputs/GPT-4/MsigDB_Response_GPT4.txt","a") as f_summary:
                f_summary.write(summary+"\n")
                f_summary.write("//\n")
            print("=====Summary=====")
            print(summary)
            
            
            # send genes and process name to GPT-4 for topic verification.
            process = summary.split("\n")[0].split("Process: ")[1]
            prompt_topic = topic(genes, process) + topic_instruction
            message_topic = [
                {"role":"system", "content":system_verify},
                {"role":"user", "content":prompt_topic}
            ]
            claims_topic = openai.ChatCompletion.create(
                engine="gpt-4-32k",
                messages=message_topic,
                temperature=0,
                )

            claims_topic = json.loads(claims_topic.choices[0]["message"]["content"])
            with open("Verification Reports/Cascade/Claims_and_Verification_for_MsigDB.txt","a") as f_claim:
                f_claim.write(str(claims_topic)+"\n")
                f_claim.write("&&\n")
            print("=====Topic Claim=====")
            print(claims_topic)
            
            verification_topic = ""
            for claim in claims_topic:
                claim_result = agentphd.inference(claim)
                verification_topic += f"Original_claim:{claim}"
                verification_topic += f"Verified_claim:{claim_result}"
                with open("Verification Reports/Cascade/Claims_and_Verification_for_MsigDB.txt","a") as f_claim:
                    f_claim.write(str(claim)+"\n")
                    f_claim.write(str(claim_result)+"\n")
                    f_claim.write("&&\n")
                print(claim)
                print(claim_result)
                
            messages.append(
                {"role":"user", "content":f"I have finished the verification for process name. Here is the verification report:\n{verification_topic} \nIf all original claims are supported, you should retain the original process name and its analytical narratives. Otherwise, you should replace the original process name with the most significant (i.e., top-1) function name (be concise) in the verification report.\nAlso revise the original summary around the updated process name."}
            )
            updated_topic = openai.ChatCompletion.create(
            engine="gpt-4-32k",
            messages=messages,
            temperature=0,
            )
            
            messages.append(updated_topic.choices[0]["message"])
            updated_topic = updated_topic.choices[0]["message"]["content"]
            # with open("updated-topic.mouse.cascade.txt","a") as f_claim:
            #     f_claim.write(updated_topic+"\n")
            #     f_claim.write("//\n")
            print("=====Updated Topic=====")
            print(updated_topic)
            
            
            # send genes and updated summary to GPT-4 for analysis verification.
            prompt_analysis = analysis(genes, summary) + analysis_instruction
            analysis_message = [
                {"role":"system", "content":system_verify},
                {"role":"user", "content":prompt_analysis}
            ]
            claims_analysis = openai.ChatCompletion.create(
                engine="gpt-4-32k",
                messages=analysis_message,
                temperature=0,
                )
            claims_analysis = json.loads(claims_analysis.choices[0]["message"]["content"])
            with open("Verification Reports/Cascade/Claims_and_Verification_for_MsigDB.txt","a") as f_claim:
                f_claim.write(str(claims_analysis)+"\n")
                f_claim.write("&&\n")
            print("=====Analysis Claim=====")
            print(claims_analysis)
            
            verification_analysis = ""
            for claim in claims_analysis:
                claim_result = agentphd.inference(claim)
                verification_analysis += f"Original_claim:{claim}"
                verification_analysis += f"Verified_claim:{claim_result}"
                with open("Verification Reports/Cascade/Claims_and_Verification_for_MsigDB.txt","a") as f_claim:
                    f_claim.write(str(claim)+"\n")
                    f_claim.write(str(claim_result)+"\n")
                    f_claim.write("&&\n")
                print(claim)
                print(claim_result)
                
            ## send verificaton report to GPT-4 and modify the gene analysis
            messages.append(
                {"role":"assistant", "content":f"I have finished the verification for the revised summary. Here is the verification report:\n{verification_analysis}\nPlease modify the summary according to the verification report again.\nIf all claims of the revised process name cannot be supported, you must propose a new brief name by summarizing the prominent biological function jointly performed by genes from the verification report.\nOtherwise, you must retain the revised process name. Don't mention the unverified claims in the updated summary."}
            )
            updated = openai.ChatCompletion.create(
                engine="gpt-4-32k",
                messages=messages,
                temperature=0,
                )
            
            update = updated.choices[0]["message"]["content"]
            with open("Outputs/GeneAgent/Cascade/MsigDB_Final_Response_GeneAgent.txt","a") as f_final:
                f_final.write(update+"\n")
                f_final.write("//\n")
            print("====Final Update====")
            print(update)
                
            with open("Verification Reports/Cascade/Claims_and_Verification_for_MsigDB.txt","a") as f_claim:
                    f_claim.write("////\n")
                
            logger.info(f"Performing@{ID}\n" +  json.dumps(messages, indent=4))
            
        except Exception as E:
            with open("Outputs/GeneAgent/Cascade/MsigDB_Final_Response_GeneAgent.txt","a") as f_final:
                f_final.write(ID + "\t")
                f_final.write(f"====There are an error {E} here.====\n")
                f_final.write("//\n")
                
            print(f"====There are an error {E} here.====")