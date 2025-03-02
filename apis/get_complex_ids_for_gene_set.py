import requests
import json

def get_complex_ids_for_gene_set(gene_set):
    gene_set = gene_set.replace(" ","")
    
    url = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/agentapi/complex/?"
    params = {
        "name": gene_set,
        "retmode": "json",
        "limit": 10
        }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return json.dumps(response.json().get("results",{}))
    else:
        return f"Error: Unable to fetch data (Status Code: {response.status_code})"


get_complex_ids_for_gene_set_doc = {
	"name": "get_complex_ids_for_gene_set",
	"description": "Given a gene set, return information on its complex ids (i.e., \"complex_ac\") separated by comma like \"a,b,c\".",
	"parameters": {
		"type": "object",
		"properties": {
			"gene_set": {
				"type": "string",
				"description": "A gene set delimitted with \",\" only to search, for example, \"x,y,z\"."
                }
            },
		"required": ["gene_set"],
	},
}


