# Covid19
Programs to help understand and fight the pandemic.

generator.py - generates dataset that can be used for contact tracing and other analysis. provides detailed configurations to model various scenarios. Generated files are named 'cov19_gen_dataset*.csv'.

cov19_con_trace.py - does contact tracing analysis for input data (data needs to be in the format generated by generator.py). Also generates a few intermediate csv files.

All configurable parameters are explained in the relevant python file by way of code comments.

There are multiple folders with data. These folders contain the raw data generated by the generator.py and also processed files generated by cov19_con_trace.py. All these folders' naming convention is of the form: 'cov19_gen_dataset_pop-X_sickper-Y_startloc-Z', where X,Y & Z are configurable parameters and indicate, respectively, population size (X), percentage of sick people in that population (Y) and number of start locations (Z). These outer folders (e.g. 'cov19_gen_dataset_pop-10_sickper-03_startloc-02') in turn contain multiple files. They are: a) cov19_gen_dataset_pop-X_sickper-Y_startloc-Z.csv: the raw data generated by generator.py b) preppd_df-cov19_gen_dataset_pop-X_sickper-Y_startloc-Z.csv: an intermediate file generated as a part of processing inside cov19_con_trace.py. Contains the same data as the raw dataset but is cleaned and ordered by time. c) travelhist_df-cov19_gen_dataset_pop-X_sickper-Y_startloc-Z.csv: contains an exploded travel history of the full population and information about overlaps in geographic location as well as time for each member of the population with the rest of the population. d) graph-cov19_gen_dataset_pop-X_sickper-Y_startloc-Z.gz: holds all the information required to create a networkx graph (which in turn is based off the travel history). The graph is in python pickle format and is compressed. e) download-cov19_gen_dataset_pop-X_sickper-Y_startloc-Z.png: contains a PNG image of the graph discussed in d. f) analysis_output_mcradius-O.txt: the final output of the cov19_con_trace.py which holds information about known infected people, vulnerable people (high risk to infection), vulnerable locations and predicted locations that could become vulnerable. O here indicates the microcell radius set as configuration in cov19_con_trace.py.