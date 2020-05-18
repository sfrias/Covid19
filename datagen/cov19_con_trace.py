'''
Does Covid 19 contact tracing analysis on data of the form: 
<name, latitude, longitude, date, time, condition>
where name = name of the person, latitude & longitude are the geographical coordinates, date
& time are the time stamp when those coordinates were recorded and finally condition indicates
whether this person is sick or healthy.

Use generator.py to generate data in the above form with various configurations.

This program assumes that the input data is in the format prescribed above.

'''

import pandas as pd
import LatLon
from LatLon import *
import networkx as nx
import matplotlib.pyplot as plt

##### All configurations start here #####

#set for lat, lon otherwise implicit default loses precision
pd.set_option('display.precision',12)

#data file path. this is the data to be analyzed.
datapath = 'cov19_gen_dataset.csv'

#stores the size of the virtual microcell around each location a person was recorded to have visited.
#this is used to calculate if two persons have breached the commonly accepted social distance limits.
#can be changed to anything, default is kept at x metres.
microcell_radius = 0.002 #in metres

##### All configurations end here   #####

##### Runtime variables #####
rawdataframe = pd.DataFrame()
sorteddf = pd.DataFrame() #same as raw data frame except all locations are sorted asc order by time of visit
persons = []
all_locs_unnormalized = [] #holds all recorded locations in an array
gx_pop_travel_hist = [] #array of nx graphs holding travel history of each member in pop

##### Methods #####

#customized printer
def printcov(str_to_print):
    print("[log]:--> " + str_to_print)

#Cleans and perpares data to be suitable for running analysis. Typically, this involves
#finding each unique person in the dataset, sorting the location records by time in an
#ascending order and others.
def dataprep():
    rawdataframe = pd.read_csv(datapath, sep=',', header=0)
    
    printcov("Sample of loaded raw data: ")
    print(rawdataframe.head(3))
    print(rawdataframe.tail(3))

    popcount = 0
    lastname = ""
    dftmp = pd.DataFrame()

    #our goal is to get each unique name and then prepare data for that.
    for index, row in rawdataframe.iterrows():
        currname = row['name']
        if(currname != lastname):
            printcov("Processing for: " + currname)
            persons.append(currname)
            df = rawdataframe.loc[rawdataframe['name'] == currname]
            printcov("# of rows found: " + str(len(df)))
            popcount = popcount + 1

            #now to sort the rows by time. We ignore the Date field as we are assuming
            #that the data is of a single day only.
            df = df.sort_values(by=['time'])
            
            #finally append this to the sorted df
            dftmp = dftmp.append(df)
            lastname = currname

    printcov("Completed prep for data.")
    #sorteddf = sorteddf.append(dftmp)
    printcov("Prepp'd data: ")
    print(dftmp.head(27))
    print(dftmp.tail(27))
    printcov("Unique people found in pop of size: " + str(popcount))
    print(persons)
    printcov("Saving prepp'd data to a file: preppd_df.csv for debugging (in current folder).")
    dftmp.to_csv("preppd_df.csv")

    return dftmp

#prepares graph data per unique person in the provided dataset and plots their travel
#history with locations and time. Also generates and adds useful attributes to nodes 
#and edges that help in further analysis. At this point, we know the total population
#size, the names of each unique person. We use this to plot a graph for analysis.
def graph_per_person(person):
    printcov("Generating graph for: " + person)
    one_persons_records = sorteddf.loc[sorteddf['name'] == person] #sorted by time in asc order
    print(one_persons_records)
    gx = nx.MultiDiGraph(person=person) #new graph for curr person

    #create all nodes
    nodeid=0
    for index, row in one_persons_records.iterrows():
        #each recorded loc is a node
        gx.add_node(nodeid,latlon=LatLon(Latitude(row['lat']),Longitude(row['lon'])))
        nodeid = nodeid+1
    
    #gx.add_edge(currnode,nextnode,time=one_persons_records.at[nid+1,'time'])
    disp_graph(gx)
    gx_pop_travel_hist.append(gx)
    
    #disp_graph(gx_pop_travel_hist)

    return

#display graphs
def disp_graph(g):
    nx.draw(g, with_labels=True)
    nx.draw_networkx_edge_labels(g, pos=nx.spring_layout(g))
    plt.show()

##### main #####
printcov("Starting Covid 19 contact tracing analysis for data in: ")
printcov(" " + datapath)

#call dataprep method
sorteddf = dataprep()

#call graph generation method for each person in the dataset
print("Initiating graph generation...")
for person in range(0,len(persons)):
    graph_per_person(persons[person])

printcov("Completed Covid 19 contact tracing analysis.")
