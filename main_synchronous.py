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
    baseline = lambda genes: f"""
    Write a critical analysis of the biological processess performed by this system of interacting proteins.
    Propose a brief name for the most prominent biological process performed by the system. 
    Put the name at the top of the analysis as "Process: <name>".
    Be concise, do not use unnecessary words.
    Be specific, avoid overly general statements such as "the proteins are involved in various cellular processes".
    Be factual, do not editorialize.
    For each important point, discribe your reasoning and supporting information.
    Here is the gene set: {genes}
    """

    ## GeneAgent - Synchronous Structure
    system_verify = "You are a helpful and objective fact-checker to verify the summary of gene set."
    analysis = lambda genes, summary: f"""
    Here is the summary for the human gene set {genes}: \n{summary}
    However, the analysis in the summary might be false. Please generate decontextualized claims for the gene analysis that need to be verified.
    Please return a JSON list only containing the generated strings of claims:
    """
    analysis_instruction = """
    Don't generate claims for the summarization, conclusion and reasoning over the previous analysis. 
    Don't generate hypotheis claims for genes like diseases, mutations, disruptions, etc.
    Mustn't generate claims containing the entire gene set or 'this system'.
    Claims should contain the gene names and their biological process functions.
    """

    ## For NeST and MsigDB
    reposits = [
        "get_complex_for_gene_set",
        "get_disease_for_single_gene",
        "get_domain_for_single_gene",
        "get_enrichment_for_gene_set",
        "get_pathway_for_gene_set",
        "get_interactions_for_gene_set",
        "get_gene_summary_for_single_gene",
        "get_pubmed_articles"
    ]

    ## For Gene Ontology
    # reposits = [
    #     "get_complex_for_gene_set",
    #     "get_disease_for_single_gene",
    #     "get_domain_for_single_gene",
    #     # "get_enrichment_for_gene_set",
    #     "get_pathway_for_gene_set",
    #     "get_interactions_for_gene_set",
    #     "get_gene_summary_for_single_gene",
    #     "get_pubmed_articles"
    # ]
    
    agentphd = AgentPhD(function_names=reposits)
    
    data = pd.read_table("Datasets/MsigDB/MsigDB.csv", header=0, index_col=None)
    for genes in data["Genes"]:
        genes = genes.replace(" ",",")

        ## send genes to GPT-4 and generate the original template of process name and analysis
        prompt_baseline = baseline(genes)
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
        print("=====Summary=====")
        print(summary)
        
        ## send process name to GPT-4 for topic verification.
        original_process = summary.split("\n")[0].split("Process: ")[1]
        updated_topic = topic_verification(genes, original_process, agentphd)
        updated_topic = updated_topic.split("\n")[0].split("Topic:")[1]
        
        ## send genes and summary to GPT-4 and verify the summary
        summary = '\n\n'.join(summary.split("\n\n")[1:])
        prompt_analysis = analysis(genes, summary) + analysis_instruction
        analysis_message = [
            {"role":"system", "content":system_verify},
            {"role":"user", "content":prompt_analysis}
        ]
        claims = openai.ChatCompletion.create(
            engine="gpt-4",
            messages=analysis_message,
            temperature=0.0,
            )
        claims = json.loads(claims.choices[0]["message"]["content"])
        print("=====Analysis Claim=====")
        print(claims)
        
        verification = ""
        for claim in claims:
            claim_result = agentphd.inference(claim)
            verification += f"Original_claim:{claim}"
            verification += f"Verified_claim:{claim_result}"
            with open("Verification Reports/Synchronous/Claims_and_Verification_for_MsigDB.txt","a") as f_claim:
                f_claim.write(str(claim)+"\n")
                f_claim.write(str(claim_result)+"\n")
                f_claim.write("&&\n")
            print(claim)
            print(claim_result)
            
        ## send verificaton report to GPT-4 and modify the gene analysis
        messages.append(
            {"role":"user", "content":f"I have finished the verification for the summary, here is the verification report:\n{verification}\nPlease propose a new brief name by using the significant biological mechanism jointly performed by most genes.\nPlease also revise the original summary accordingly.\nDon't mention uverified claims in the summary."}
        )
        
        updated_summary = openai.ChatCompletion.create(
            engine="gpt-4-32k",
            messages=messages,
            temperature=0.0,
            )
        messages.append(updated_summary.choices[0]["message"])
        updated_summary = updated_summary.choices[0]["message"]["content"]
        # with open("updated-summary.nest.sync.result.txt","a") as f_update:
        #     f_update.write(updated_summary+"\n")
        #     f_update.write("//\n")
        print("====Updated Summary====")
        print(updated_summary)
        
        new_name = updated_summary.split("\n")[0].split("Process:")[1]
        
        
        ## compare the consistence of these two names via GPT-4
        messages.append(
            {"role":"user", "content":f"Is {new_name} similar to {updated_topic} based on their biological functions? Plase answer yes or no."}
            )
        messages.append(
            {"role":"user", "content":f"If your answer is yes, select the one involving biological mechanism at a finer granularity.\nIf your answer is no, propose a new professional term that consists of the literal of two terms. The generated name should be concise and reflect the core function of original terms. Don't use any abbreviations and spliced unreadable words."}
            )
        messages.append(
            {"role":"user", "content":f"Please also revise the summary accordingly.\nDon't mention those claims that are unverified in the summary.\nPut the final name at the top of the analysis as \"Process: <name>\"."}
            )
        update = openai.ChatCompletion.create(
			engine="gpt-4-32k",
			messages=messages,
			temperature=0.0,
			)
        update = update.choices[0]["message"]["content"]
        with open("Outputs/GeneAgent/Synchronous/MsigDB_Final_Response_GeneAgent.txt","a") as f_final:
            f_final.write(update+"\n")
            f_final.write("//\n")
        print("====Final Update====")
        print(update)
        
        with open("Verification Reports/Synchronous/Claims_and_Verification_for_MsigDB.txt","a") as f_claim:
            f_claim.write("////\n")