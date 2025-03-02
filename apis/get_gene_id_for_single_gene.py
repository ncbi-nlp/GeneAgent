import json
import requests
import time

def get_gene_id_for_single_gene(gene, specie):
	base_url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
	term = gene + " AND " + specie
	search_params = {
		"db": "gene",
		"term": term,
		"retmode": "json",
		"retmax": 5,
		"sort": "relevance"
	}
	
	search_response = requests.get(base_url_search, params=search_params)
	gene_ids = search_response.json().get('esearchresult', {}).get("idlist", [])

	return json.dumps(gene_ids)


get_gene_id_for_single_gene_doc = {
	"name": "get_gene_id_for_single_gene",
	"description": "Given a single gene name, return the most related gene ID (for instance \"123\") in the given specific specie.",
	"parameters": {
		"type": "object",
		"properties": {
			"gene": {
				"type": "string",
				"description": "A single gene name to search.",
			},
   			"specie": {
				"type": "string",
				"description": "A specie name to search. Only have the human specie (Homo) and mouse specie (Mus) now.",
				"enum": ["Homo","Mus"]
			},
		},
		"required": ["gene","specie"],
	},
}


# a = get_gene_id("CDKN1A","Homo")
# print(a)