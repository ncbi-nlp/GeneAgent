import json
import pandas as pd

def get_domain_name_for_domain_id(domain_id):
     
    domain_dict = {}
    data = pd.read_table("backend_domains.tsv", header=0, index_col=None, sep="\t")
    for ID, name in zip(data["domainID"], data["domainName"]):
        domain_dict[ID] = name
        
    if domain_id in domain_dict.keys():
        return json.dumps(domain_dict[domain_id])
    else:
        return None
        
    

get_domain_name_for_domain_id_doc = {
	"name": "get_domain_name_for_domain_id",
	"description": "Given a domain id, return information on its corresponding domain name.",
	"parameters": {
		"type": "object",
		"properties": {
			"domain_id": {
				"type": "string",
				"description": "A domain id to search."
				}
            },
		"required": ["domain_id"],
	},
}


