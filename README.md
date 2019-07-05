# Non-Parametric Class Completeness Estimators for Collaborative Knowledge Graphs

## Pre-Requisites

* Necessary python requirements: `pip install -r requirements.txt`
* graph-tool [Website](https://graph-tool.skewed.de/), [Installation intructions](https://git.skewed.de/count0/graph-tool/wikis/installation-instructions)

## Data Pipeline

The following tasks are dependent on each other and can be run without any parameters in the following order.

### Export Edits from Edit History

[0_export_edits.sql](0_export_edits.sql)
After the XML Dump of Wikidata is loaded in a SQL Database (with e.g. [MWDumper](https://www.mediawiki.org/wiki/Manual:MWDumper)). The above mentioned query exports all edits.

###Data Preparation

[1_create_inmemory_graph.py](1_create_inmemory_graph.py): Extract an inmemory representation of Wikidata.
[2_extract_mentions.py](2_extract_mentions.py): Extract the mentions from the edits with help of the InMemory Graph.

### Calculate Estimates and Convergence

[3_calculate_estimates.py](3_calculate_estimates.py): Calculate the Estimates of all Classes [4_draw_graphs.py](4_draw_graphs.py): Draw the graphs and calculate the Convergence for all Classes.

##Estimator and Metrics

The estimators and metrics can be found as independent methods, ready to use in [estimators.py](estimators.py) and [metrics.py](metrics.py) respectively.

## Results

[result.html](results.html)

For all classes with at least 5000 observations we calculated the convergence metric and draw the graph. Find all classes listed in [result.html](results.html). Additionally we also provide the results in a CSV [result.csv](results.csv) (tab separated, utf-8).


