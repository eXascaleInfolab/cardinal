# Non-Parametric Class Completeness Estimators for Collaborative Knowledge Graphs

## Pre-Requisites

* Necessary Python requirements: `pip install -r requirements.txt`
* [`graph-tool` Python Package](https://graph-tool.skewed.de/): This can not be installed through pip -> [Installation intructions](https://git.skewed.de/count0/graph-tool/wikis/installation-instructions)

## Data Pipeline

### Data Sources
The following tasks are dependent on each other and can be run without any parameters, the default parameters expect the datasets to be present in the subfolder `/data`. The necessary origin datasets are not anymore available at the source:

- Edit History: Any recent Version of `*-pages-meta-history1.xml` at https://dumps.wikimedia.org/wikidatawiki can be used. (see below) 
- JSON Dump: https://zenodo.org/record/3268725 (accessed at https://dumps.wikimedia.org/wikidatawiki/entities/20180813)

Additionaly we provide the data for every intermediary step as download at https://zenodo.org/record/3268818.

### 1. Export Edits from Edit History

* [0_export_edits.sql](0_export_edits.sql)

    1. Load the XML Dump of Wikidata in a SQL Database (with e.g. [MWDumper](https://www.mediawiki.org/wiki/Manual:MWDumper)).
    2. The provided query exports all edits. (The query can be restricted to edits before the timestamp "2018-10-01" to recreate the output presented in the paper.) 

### 2. Data Preparation

* [1_create_inmemory_graph.py](1_create_inmemory_graph.py): Extract an in-memory representation of Wikidata.
* [2_extract_observations.py](2_extract_observations.py): Extract the observations from the edits with help of the in-memory Graph.

### 3. Calculate Estimates and Convergence

* [3_calculate_estimates.py](3_calculate_estimates.py): Calculate the Estimates of all Classes.
* [4_draw_graphs.py](4_draw_graphs.py): Draw the graphs and calculate the Convergence for all Classes.

## Estimator and Metrics

The estimators and metrics are available at [estimators.py](estimators.py) and [metrics.py](metrics.py) respectively.

## Results

[cardinal.exascale.info](https://cardinal.exascale.info)

For all classes with at least 5000 observations we calculated the convergence metric and draw the graph. Find all classes listed on [cardinal.exascale.info](https://cardinal.exascale.info). 

Additionally we also provide the results as CSV [result.csv](results.csv) (tab separated, utf-8) file.
