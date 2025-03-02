import json
import pandas as pd

def get_disease_name_for_disease_id(disease_id):
     
    disease_dict = {}
    data = pd.read_table("backend_diseases.tsv", header=0, index_col=None, sep="\t")
    for ID, name in zip(data["DiseaseID"], data["DiseaseName"]):
        disease_dict[ID] = name
        
    if disease_id in disease_dict.keys():
        return json.dumps(disease_dict[disease_id])
    else:
        return None
        
    

get_disease_name_for_disease_id_doc = {
	"name": "get_disease_name_for_disease_id",
	"description": "Given a disease id, return information on its corresponding disease name.",
	"parameters": {
		"type": "object",
		"properties": {
			"disease_id": {
				"type": "string",
				"description": "A disease id to search."
				}
            },
		"required": ["disease_id"],
	},
}


