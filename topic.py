import json
import time
import pandas as pd

import openai
## Replace with your own OpenAI model and key
openai.api_type = "azure"
openai.api_base = "***************"
openai.api_version = "*****************"
openai.api_key = "**************************" 


## topic verification
system_verify = "You are a helpful and objective fact-checker to verify the process name of gene set."
topic = lambda genes, process: f"""
Here is the vanilla process name for the human gene set {genes}:\n{process}
However, the process name might be false. Please generate decontextualized claims for the process name that need to be verified.
Please return JSON list only containing the generated strings of claims:
"""
topic_instruction = """
Generate claims of affirmative sentences about the prominent biological process for the entire gene set.
Don't generate negative sentences in claims for the entire gene set.
Don't generate claims for the single gene or incomplete gene set.
Don't generate hypotheis claims over the previous analysis like diseases, mutations, disruptions, etc.
Please replace the statement like 'these genes', 'this system' with the entire gene set.
"""

def topic_verification(genes, process_name, agentphd):  
    
    ## send genes and summary to GPT-4 and generate claims for verifying topic name
    prompt_topic = topic(genes, process_name) + topic_instruction
    message = [
        {"role":"system", "content":system_verify},
        {"role":"user", "content":prompt_topic}
    ]
    claims = openai.ChatCompletion.create(
        engine="gpt-4",
        messages=message,
        temperature=0.0,
        )
    claims = json.loads(claims.choices[0]["message"]["content"])
    print("=====Topic Claim=====")
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
        
    ## send verificaton report to GPT-4 and modify the original process name
    message.append(
        {"role":"assistant", "content":f"There should be only one most significant function name. If the process name is direclty supported in all verifications, the significant function is the name that most similar to the original process name but reflects more specific biological regulation mechanism. Otherwise, it is the first (top-1) function name in verifications."}
    )
    message.append(
        {"role":"user", "content":f"I have finished the verification for the process name, here is the verification report:{verification}\nPlease replace the process name with the most significant function of gene set.\nPlease start a message with \"Topic:\" and only return the brief revised name."}
    )
    updated = openai.ChatCompletion.create(
        engine="gpt-4-32k",
        messages=message,
        temperature=0.0,
        )

    # messages.append(updated_topic.choices[0]["message"])
    updated = updated.choices[0]["message"]["content"]
    # with open("updated-topic.nest.result.sync.txt","a") as f_update:
    #     f_update.write(updated+"\n")
    #     f_update.write("//\n")
    print("=====Updated Topic=====")
    print(updated)
    
    return updated
