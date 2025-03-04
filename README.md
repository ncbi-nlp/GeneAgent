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
Process: Transmembrane Receptor Protein Tyrosine Kinase Activity
The system of interacting proteins encoded by the genes ERBB2, ERBB4, FGFR2, FGFR4, HRAS, and KRAS primarily facilitates transmembrane receptor protein tyrosine kinase activity, a critical pathway for cellular communication and regulation.
1. **Receptor Activation and Dimerization**:
   - **ERBB2 (HER2)**: This gene encodes a member of the epidermal growth factor receptor (EGFR) family. ERBB2 does not have a ligand binding domain of its own and cannot bind growth factors directly. Instead, it forms heterodimers with other ligand-bound EGF receptor family members, stabilizing ligand binding and enhancing kinase-mediated activation of downstream signaling pathways, such as those involving mitogen-activated protein kinase (MAPK) and phosphatidylinositol-3 kinase (PI3K) [source: RefSeq, Jul 2008].
   - **ERBB4 (HER4)**: This gene encodes a member of the Tyr protein kinase family and the EGFR subfamily. ERBB4 binds to and is activated by neuregulins and other factors, inducing a variety of cellular responses including mitogenesis and differentiation [source: Gene Summary].
2. **Signal Transduction**:
   - **FGFR2 (Fibroblast Growth Factor Receptor 2)**: This gene encodes a receptor that interacts with fibroblast growth factors, initiating a cascade of downstream signals that influence mitogenesis and differentiation. FGFR2 is crucial for processes such as cell growth, differentiation, and angiogenesis [source: RefSeq, Jan 2009].
   - **FGFR4 (Fibroblast Growth Factor Receptor 4)**: This gene encodes a receptor involved in the regulation of several pathways, including cell proliferation, differentiation, migration, lipid metabolism, and glucose uptake. FGFR4 interacts with fibroblast growth factors, setting in motion downstream signals that influence mitogenesis and differentiation [source: RefSeq, Aug 2017].
3. **Molecular Switches**:
   - **HRAS**: This gene encodes a small GTPase that acts as a molecular switch in RTK signaling pathways. HRAS binds GTP and GDP and has intrinsic GTPase activity, regulating cell proliferation, survival, and differentiation [source: Gene Summary].
   - **KRAS**: This gene encodes a small GTPase involved in various malignancies. KRAS functions as a molecular switch in RTK signaling pathways, playing a role in cell proliferation, survival, and differentiation [source: RefSeq, Jul 2008].
4. **Pathological Implications**:
   - Dysregulation of these proteins, through overexpression, mutation, or aberrant activation, is implicated in various cancers. For instance, overexpression of ERBB2 is a well-known driver in breast cancer, while mutations in KRAS are common in pancreatic, colorectal, and lung cancers.
In summary, the system of proteins encoded by ERBB2, ERBB4, FGFR2, FGFR4, HRAS, and KRAS orchestrates transmembrane receptor protein tyrosine kinase activity, a pivotal process for cellular communication and regulation. This pathway's precise control is vital for normal cellular function, and its dysregulation is a hallmark of many cancers.
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
This tool shows the results of research conducted in the Computational Biology Branch, DIR/NLM. The information produced on this website is not intended for direct diagnostic use or medical decision-making without review and oversight by a clinical or genomics professional. Individuals should not change their health behavior solely on the basis of information produced on this website. NIH does not independently verify the validity or utility of the information produced by this tool. If you have questions about the information produced on this website, please see a health care professional. More information about DIR's disclaimer policy is available.

