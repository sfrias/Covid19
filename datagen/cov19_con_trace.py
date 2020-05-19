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
import time
from copy import deepcopy

##### All configurations start here #####

#set for lat, lon otherwise implicit default loses precision
pd.set_option('display.precision',12)

#data file path. this is the data to be analyzed.
datapath = 'cov19_gen_dataset.csv'#'cov19_gen_dataset_10k.csv'

#stores the size of the virtual microcell around each location a person was recorded to have visited.
#this is used to calculate if two persons have breached the commonly accepted social distance limits.
#can be changed to anything, default is kept at x metres.
microcell_radius = 0.002 #in metres

#controls whether graphs are visually displayed or not. If running on linux ensure X Windows is available.
#0 = graphs are displayed in ui. 1 = no graphs are displayed.
ui = 1

##### All configurations end here   #####

##### Runtime variables #####
rawdataframe = pd.DataFrame()
sorteddf = pd.DataFrame() #same as raw data frame except all locations are sorted asc order by time of visit
persons = []
all_locs_unnormalized = [] #holds all recorded locations in an array
gxarry_pop_travel_hist = [] #array of nx graphs holding travel history of each member in pop
undir_gxarray_pop_travel_hist = []#same graph as gxarry_pop_travel_hist except it is undirected

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
    dftmp = dftmp.reset_index(drop=True)
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
    one_persons_records = one_persons_records.reset_index(drop=True)
    print(one_persons_records)
    gx = nx.MultiDiGraph(name=person) #new graph for curr person

    #create all nodes
    nodeid=0
    for index, row in one_persons_records.iterrows():
        #each recorded loc is a node
        gx.add_node(nodeid,latlon=LatLon(Latitude(row['lat']),Longitude(row['lon'])))
        nodeid = nodeid+1
    
    #now let's add edges for the nodes
    print("Adding edges for: " + str(nx.number_of_nodes(gx)) + " nodes...")
    print(gx.nodes())
    for x in range(0,nx.number_of_nodes(gx)):
        y = x + 1
        if(y == nx.number_of_nodes(gx)):
            print("reached end node")
            break
        else:
            gx.add_edge(x,y,time=one_persons_records.at[y,'time'])

    print("Completed adding edges for: " + str(person) + ". Graph complete.")

    disp_graph(gx)
    gxarry_pop_travel_hist.append(gx)

    return

#finds overlapping locations with time for the population and also marks such
#locations with a new attribute so that we can easily analyze them later. We also
#create a new undirected graph that has all overlaps available. There shall be one
#such overlap graph per person in the population.
def overlaps_for_pop(gxall):
    printcov("Finding overlaps within population's location history")
    for x in range(0, len(gxall)):
        #get the 1st person and find overlaps of each of their loc
        #with each loc of each other person in the population.
        
        #we convert the graph to an undirected copy since mixed graphs are
        #not possible in nx. We'll use both versions for later analysis. Note
        #that the loc overlap calc doesnt need undirected graph. We shall create
        #a new undirected edge for each overlap and that is why we need to
        #convert to undirected graph
        undirectedgxcurr = gxall[x].to_undirected() #get this person's graph
        disp_graph(undirectedgxcurr)

        """ if(x == len(gxall)-1):
            #we've reached the last person (graph) in the array.
        else: """
        #compare current person graph with all others for loc overlaps
        #first copy out the graph container
        gxallminuscurr = []
        for cv in range(0,len(gxall)):
            newgx = deepcopy(gxall[cv])
            gxallminuscurr.append(newgx)

        #gxallminuscurr = copy.deep_copy(gxall)
        gxallminuscurr.pop(x)#remove current persons graph before cmp
        for y in range(0, len(gxallminuscurr)):
            undirectedgxnext = gxallminuscurr[y].to_undirected()
            find_overlap(undirectedgxcurr,undirectedgxnext)
            
    printcov("Completed overlap extractions.")
    return

#finds overlapping locations between two graphs
def find_overlap(undgx_curr, undgx_next):
    #get 'latlon' attributes of all nodes
    printcov("Processing overlaps. Anchor graph: " + str(undgx_curr.graph['name']) + " and Comparison graph: " + str(undgx_next.graph['name']))
    gxcurr_nodeattrib = nx.get_node_attributes(undgx_curr,'latlon')
    gxnext_nodeattrib = nx.get_node_attributes(undgx_next,'latlon')
    printcov("Node attributes for overlap calc are:\n")
    print("curr anchor node: " + str(gxcurr_nodeattrib))
    print("\n")
    print("comparison  node: " + str(gxnext_nodeattrib))

    return

#allows to validate all graphs. For each graph, walks it, explodes nodes and edges.
def test_all_graphs(g):
    printcov("=========> Testing all graphs: ")
    for i in range(0, len(g)):
        print(nx.info(g[i]))

        print(" - Nodes:")
        print(g[i].nodes)
        for x1 in range(0, len(g[i].nodes)):
            print("Node id: " + str(x1) + str(g[i].nodes[x1]))
        
        print(" - Edges:")
        print(g[i].edges)
        print("Edge attributes: " + str(nx.get_edge_attributes(g[i],'time')))
        
        print('------------------------------------------')
    printcov("=========> Testing complete.")
    return

#display graphs
def disp_graph(g):
    if(ui == 0):
        nx.draw(g, with_labels=True)
        nx.draw_networkx_edge_labels(g, pos=nx.spring_layout(g))
        plt.show()

##### main #####
printcov("Starting Covid 19 contact tracing analysis for data in: ")
printcov(" " + datapath)
printcov("Configurations are: ")
print("Microcell radius for overlap calc: " + str(microcell_radius))
print("Graph display control is: " + str(ui) + ".   0 = ON / 1 = OFF.")
print('-------------------------------------')
time.sleep(7.7)

#call dataprep method
sorteddf = dataprep()

#call graph generation method for each person in the dataset
print("Initiating graph generation...")
for person in range(0,len(persons)):
    graph_per_person(persons[person])

#gxarry_pop_travel_hist was filled in graph_per_person
test_all_graphs(gxarry_pop_travel_hist)

overlaps_for_pop(gxarry_pop_travel_hist)

printcov("Completed Covid 19 contact tracing analysis.")
