# Project Overview
## Title
GeneAgent: Self-verification Language Agent for Gene Set Analysis using Domain Databases
## Abstract
GeneAgent is a first-of-kinds language agent built upon GPT-4 to automatically interact with domain-specific databases to annotate functions for gene sets. GeneAgent generates interpretable and contextually accurate biological process names for user-provided gene sets, either aligning with significant enrichment analyses or introducing novel terms. At the core of GeneAgent’s functionality is a self-verification setting. This mechanism autonomously interacts with various expert-curated biological databases through Web APIs. By utilizing relevant domain-specific information, GeneAgent performs fact verification and provides objective evidence to support or refute the raw LLM output, reducing hallucination and enabling reliable, evidence-based insights into gene function.
<p align="center" width="50%">
  <img width="80%" src="https://github.com/ncbi-nlp/GeneAgent/blob/main/workflow.geneagent.svg">
</p>

# Requirement
	python 3.11.0
	openai 0.28.0
	torch  1.13.0
	numpy  1.26.3
	pandas 2.1.4
	requests  2.31.0 
	requests-oauthlib  1.3.1
 	seaborn 0.13.2
  tiktoken 0.11.0

# Datasets
- Gene Ontology: contain 1000 gene sets from the GO:BP branch of the gene ontology database
- MsigDB: contain 56 gene sets including the hallmark gene sets
- NeST: contain 50 gene sets sampled from the human cancer proteomic data
>[!TIP]
>The original datasets could be found at
>* https://github.com/idekerlab/llm_evaluation_for_gene_set_interpretation/blob/main/data/
>* https://github.com/monarch-initiative/talisman-paper/tree/main/genesets/human

# Configuration:
## Installation 
1. Apply an OpenAI Key from the Azure OpenAI service to activate the access of LLMs, e.g., GPT-4.
   
   OpenAI Documentation: https://learn.microsoft.com/en-us/azure/ai-services/

 2. Create a virtual environment on your GPU terminate by using the anaconda command:
    ```
    conda create -n {envname} python=3.11
    ```
  4. Activate the environment by using the command:
     ```
     conda activate {envname}
     ```
   5. Install the required packages one by one with the command:
      ```
      python install {package} == {version}
      ```
      
## Download 
1. Create a directory for GeneAgent in your own workplace
 2. Download this respoisit directly to your directory or git the respoisit by:
    ```
    git@github.com:ncbi-nlp/GeneAgent.git
    ```
## Replace the openai key
1. Go to the created directory of GeneAgent
   ```
   cd {directory}
   ```
 2. Open the **main_cascade.py** and the **worker.py** respectively to replace the **openai.api_key** with your own API Key as well as other required parameters **openai.api_base** and **openai.api_version**.
	```
 	openai.api_key=YOUR_OWN_OPENAI_KEY
	openai.api_base=YOUR_OWN_OPENAI_BASE_SETTING
	openai.api_version=YOUR_OWN_OPENAI_API_VERSION
 	```
  >[!TIP]
   >If you need to run the variants of GeneAgent, such as chain-of-thought **main_CoT.py** and the summarization for multiple biological terms **main_summary.py**, please also make a key replacement accordingly.

# Execute
## Running
Type following command in your virtual environment.
```
python main_cascade.py
```
The results will be stored accordingly.
 >[!TIP]
  >If you want to evaluate your own gene sets, save them to **Dataset** directory and change the directory path in the **main_cascade.py**
>Also, the output path can be changed according to your preference.

## Example outputs
```
Process: MAPK Signaling Pathway
The proteins encoded by the genes ERBB2, ERBB4, FGFR2, FGFR4, HRAS, and KRAS are all integral components of the MAPK signaling pathway, which is crucial for cell growth, differentiation, and survival.
ERBB2 and ERBB4 are members of the epidermal growth factor receptor (EGFR) family of receptor tyrosine kinases (RTKs). ERBB2 is unique in that it has no known ligands, and it prefers to form heterodimers with other EGFR family members, enhancing their kinase activity. ERBB4 is activated by neuregulins and other factors and induces a variety of cellular responses including mitogenesis and differentiation.
FGFR2 and FGFR4 are part of the fibroblast growth factor receptor (FGFR) family of RTKs. They are activated by fibroblast growth factors, leading to receptor dimerization and autophosphorylation. This triggers downstream signaling pathways that regulate cellular processes such as proliferation, differentiation, and migration.
HRAS and KRAS are GTPases that act as molecular switches in RTK signaling. They are activated by guanine nucleotide exchange factors (GEFs) that catalyze the exchange of GDP for GTP. Once activated, RAS proteins can interact with a variety of effector proteins to propagate the signal downstream.
The interaction between these proteins forms a complex network of signaling events that regulate key cellular processes. Dysregulation of this system, such as mutations that lead to constitutive activation of RTKs or RAS proteins, can result in uncontrolled cell growth and cancer. Therefore, understanding the precise mechanisms of MAPK signaling and its regulation is crucial for the development of targeted cancer therapies.
```
## Evaluate the outputs
Open **evaluate.ipynb** to run the corresponding cells based on your requirements.

# Demonstration website
A demonstration website with an open-access permissions is available at https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/GeneAgent/.
<p align="center" width="50%">
  <img width="80%" src="https://github.com/ncbi-nlp/GeneAgent/blob/main/homepage.geneagent.jpg">
</p>

# Acknowledgements
This work was supported by the Intramural Research Programs of the National Institutes of Health, National Library of Medicine.

# Disclaimer
This tool shows the results of research conducted in the Computational Biology Branch, NLM. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical or genomics professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about NLM's disclaimer policy is available.

# Zenodo identifier
[DOI: 10.5281/zenodo.15008591](https://zenodo.org/records/15008591)

