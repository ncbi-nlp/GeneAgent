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

    ## GeneAgent - Joint Structure
    system_verify = "You are a helpful and objective fact-checker to verify the summary of gene set."
    analysis = lambda genes, summary: f"""
    Here is the summary for the human gene set {genes}: \n{summary}
    However, the analysis in the summary might be false. Please generate decontextualized claims for the gene analysis that need to be verified.
    Please return a JSON list only containing the generated strings of claims:
    """
    analysis_instruction = """
    Must generate claims containing the entire gene set.
    Don't generate unworthy claims such as the summarization and reasoning over the previous analysis. 
    Don't generate hypotheis claims for genes like mutations, disruptions, etc.
    Claims should contain the gene names and their biological process functions.
    Please replace the statement like 'these genes', 'this system' with the entire gene set.
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
			engine="gpt-4-32k",
			messages=messages,
			temperature=0.0,
			)
        messages.append(summary.choices[0]["message"])
        summary = summary.choices[0]["message"]["content"]
        print("=====Summary=====")
        print(summary)
        
        ## send genes and summary to GPT-4 and verify the summary
        prompt_analysis = analysis(genes, summary) + analysis_instruction
        analysis_message = [
            {"role":"system", "content":system_verify},
            {"role":"user", "content":prompt_analysis}
        ]
        claims = openai.ChatCompletion.create(
            engine="gpt-4-32k",
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
            with open("Verification Reports/Joint/Claims_and_Verification_for_MsigDB.txt","a") as f_claim:
                f_claim.write(str(claim)+"\n")
                f_claim.write(str(claim_result)+"\n")
                f_claim.write("&&\n")
            print(claim)
            print(claim_result)
            
        ## send verificaton report to GPT-4 and modify the gene analysis
        messages.append(
            {"role":"assistant", "content":f"There should be only one most significant function name as summarized in your findings. If the process name is verified as truth, the significant function is the name that is most similar to the original process name but reflects more specific biological regulation mechanism. Otherwise, it is the first (top-1) function name in verifications."}
        )
        messages.append(
            {"role":"user", "content":f"I have finished the verification for the summary, here is the verification report:\n{verification}\nPlease revise the process name by using the most significant biological mechanism in verifications.\nPlease also revise the summary accordingly.\nDon't mention uverified claims in the summary."}
        )
        
        updated_summary = openai.ChatCompletion.create(
            engine="gpt-4-32k",
            messages=messages,
            temperature=0.0,
            )
        messages.append(updated_summary.choices[0]["message"])
        updated_summary = updated_summary.choices[0]["message"]["content"]
        with open("Outputs/GeneAgent/Joint/MsigDB_Final_Response_GeneAgent.txt","a") as f_update:
            f_update.write(updated_summary+"\n")
            f_update.write("//\n")
        print("====Updated Summary====")
        print(updated_summary)
        
        with open("Verification Reports/Joint/Claims_and_Verification_for_MsigDB.txt","a") as f_claim:
            f_claim.write("////\n")