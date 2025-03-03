import openai
## Replace with your own OpenAI model and key
openai.api_type = "azure"
openai.api_base = "***************"
openai.api_version = "*****************"
openai.api_key = "**************************" 

import os
import time
import json

import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# logger = logging.getLogger('AgentLogger')
# logger.setLevel(logging.INFO)

# log_filename = 'logs.txt'
# file_handler = RotatingFileHandler(log_filename, maxBytes=10000000, backupCount=5)
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

# timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

from apis.get_complex_for_gene_set import get_complex_for_gene_set, get_complex_for_gene_set_doc 
from apis.get_disease_for_single_gene import get_disease_for_single_gene, get_disease_for_single_gene_doc
from apis.get_domain_for_single_gene import get_domain_for_single_gene, get_domain_for_single_gene_doc
from apis.get_enrichment_for_gene_set import get_enrichment_for_gene_set, get_enrichment_for_gene_set_doc
from apis.get_pathway_for_gene_set import get_pathway_for_gene_set, get_pathway_for_gene_set_doc 
from apis.get_interactions_for_gene_set import get_interactions_for_gene_set, get_interactions_for_gene_set_doc
from apis.get_gene_summary_for_single_gene import get_gene_summary_for_single_gene, get_gene_summary_for_single_gene_doc
 
from apis.get_pubmed_articles import get_pubmed_articles, get_pubmed_articles_doc

func2info = {
    "get_complex_for_gene_set": [get_complex_for_gene_set, get_complex_for_gene_set_doc],
	"get_disease_for_single_gene": [get_disease_for_single_gene, get_disease_for_single_gene_doc],
	"get_domain_for_single_gene": [get_domain_for_single_gene, get_domain_for_single_gene_doc],
	"get_enrichment_for_gene_set": [get_enrichment_for_gene_set, get_enrichment_for_gene_set_doc],
	"get_pathway_for_gene_set": [get_pathway_for_gene_set, get_pathway_for_gene_set_doc],
	"get_interactions_for_gene_set": [get_interactions_for_gene_set, get_interactions_for_gene_set_doc],
	"get_gene_summary_for_single_gene": [get_gene_summary_for_single_gene, get_gene_summary_for_single_gene_doc],
	"get_pubmed_articles": [get_pubmed_articles, get_pubmed_articles_doc]
}


class AgentPhD:
	def __init__(self, function_names):
		self.name2function = {function_name: func2info[function_name][0] for function_name in function_names}
		self.function_docs = [func2info[function_name][1] for function_name in function_names]

	def inference(self, claim):
		messages = [
			{
				"role": "system",
				"content": "You are a helpful fact-checker. Your task is to verify the claim using the provided tools. If you have finished the verification, please start a message with \"Report:\" and return your findings at the begining along with the evidence."
			},
			{
				"role": "user",
				"content": f"\nHere is the claim:\n{claim}\n The verification for the biological function should be factual."
			} 
		]

		loop = 0
		while loop < 10:
			loop += 1
			# logger.info(f"Input@{loop}\n" +  json.dumps(messages, indent=4))
			time.sleep(2)
			completion = openai.ChatCompletion.create(
				engine="gpt-4-32k",
				messages=messages,
				functions=self.function_docs,
				temperature=0,
			)

			message = completion.choices[0]["message"]
			# logger.info(f"Output@{loop}\n" +  json.dumps(message, indent=4))

			if "function_call" in message:
				try:
					function_name = message["function_call"]["name"]
					function_params = json.loads(message["function_call"]["arguments"])
					function_to_call = self.name2function[function_name]
					function_response = function_to_call(**function_params)
					function_response = f"Function has been called with params {function_params}, and returns {function_response}."

					messages.append(
						{
							"role": "function",
							"name": function_name,
							"content": function_response
						},
					)

				except Exception as E:
					messages.append(
						{
							"role": "function",
							"name": function_name,
							"content": f"Function has been called with params {function_params}, but returned error: {E}. Please try again with the correct parameter.",
						}
					)
			
			else:
				try:
					if "Report: " in message["content"]:
						report = message["content"].split("Report: ")[-1]
						return report
					
					else:
						messages.append(
							{
								"role": "user",
								"content": f"If you have finished the verification, please start a message with \"Report:\" and return your findings at the begining along with the evidence.",
							}
						)
      
				except Exception as E:
					messages.append(
						{
							"role": "assistant",
							"content": f"Claim has been verified, but returned error: {E}. Please try it again.",
						}
					)

		return "Failed."	

# if __name__ == "__main__":
# 	reposits = [
# 	"get_complex_ids_for_gene_set",
# 	"get_disease_id_for_single_gene",
# 	"get_domain_id_for_single_gene",
# 	"get_enrichment_for_gene_set",
# 	"get_pathway_for_gene_set",
# 	"get_complex_names_for_complex_ids",
# 	"get_disease_name_for_disease_id",
# 	"get_domain_name_for_domain_id",
# 	"get_interactions_for_gene_set",
# 	"get_gene_summary_for_single_gene",
# 	"get_pubmed_articles"
# 	]

# 	agentphd = AgentPhD(function_names=reposits)
# 	test = agentphd.inference("TOR1A encodes a member of the AAA protein family and plays a role in synaptic vesicle recycling regulation.")
# 	print(test)