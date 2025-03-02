import requests
import json
import pandas as pd

def get_complex_names_for_complex_ids(complex_acs):
    complexDict = {}
    complexName = []
    data = pd.read_table("backend_complex.tsv", header=0, index_col=None, sep="\t")
    for key, value in zip(data["Complex ac"], data["Recommended name"]):
        complexDict[key] = value

    for complex_ac in complex_acs.split(","):
        if complex_ac in complexDict.keys():
            complexName.append(complexDict[complex_ac])
        else:
            continue

    return json.dumps(complexName)

get_complex_names_for_complex_ids_doc = {
	"name": "get_complex_names_for_complex_ids",
	"description": "Given several complex ids separated by \",\", return the most representative complex names in the gene set.",
	"parameters": {
		"type": "object",
		"properties": {
			"complex_acs": {
				"type": "string",
				"description": "Some complex ids delimited with \",\" (no whitespace) to search, for example \"x,y,z\"."
				}
            },
		"required": ["complex_acs"],
	},
}


