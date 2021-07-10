#!/usr/bin/python3

from z3 import *
import argparse
import itertools
import time


def convert(graph,s,t):
    l = []
    for r in graph:
        l.append(r[0])
        l.append(r[1])
    #l = list(set(l))
    l.sort()
    d=dict()
    d[l[0]]=0
    k=l[0]
    idx=1
    for i in range(1,len(l)):
        if(k!=l[i]):
            d[l[i]]=idx
            k=l[i]
            idx+=1
    
    l=[]
    for i in range(0,len(graph)):
        l.append((d[graph[i][0]],d[graph[i][1]]))

    return (l,d[s],d[t],len(d))


def encode(edges,graph_c, Q):
	ls=[]
	for edge in graph_c:
		ls.append(Implies(And(edges[edge[0]][edge[1]],Q[edge[1]]),Q[edge[0]]))
		ls.append(Implies(And(edges[edge[0]][edge[1]],Q[edge[0]]),Q[edge[1]]))
	
	return And(ls)


def initialize_paths(edges,graph_c,n):
	# Return a list of list s.t. ls[i][j] = edges[i][j] if an edge exists b/w i and j ; else ls[i][j] = Not(edges[i][j])
	ls = []
	mapping=[]
	count=0
	for i in range(n): 
		mapping.append([])
		for j in range(n):
			if (i!=j):
				mapping[i].append(count)
				ls.append(Not(edges[i][j]))
			else:
				mapping[i].append(count)
				ls.append(edges[i][j])
			count+=1

	for edge in graph_c:
	
		ls[mapping[edge[0]][edge[1]]] = edges[edge[0]][edge[1]]
		ls[mapping[edge[1]][edge[0]]] = edges[edge[1]][edge[0]]
	
	

	return [ls,mapping]	



#e_i_j represents that a path b/w i and j exists

def find_minimal(graph, s, t):
	# convert graph into an easier to interpret representation with 0-based indexing
	graph_c=convert(graph,s,t)
	s=graph_c[1]
	t=graph_c[2]
	n=graph_c[3]
	graph_c=graph_c[0]
	
	edges=[]
	# Create bools for edges
	for i in range(n):
		edges.append([])
		for j in range(n):
			edges[i].append(Bool("e_{}_{}".format(i,j)))
	

	# Create the Q i.e Q[i] represents a bool  to show if there is a path b/w i and t
	Q = []
	for i in range(n):

		#if(i<t and (i,t) in graph_c):
		Q.append(Bool("q_{}".format(i)))
	
	[edge_constraints,mapping] = initialize_paths(edges,graph_c,n)
	
	F = encode(edges,graph_c, Q)
	F = And(F,Not(Q[s]),Q[t])
	removed=[]
	edges_t = []
	
	extra=[]
	##FINDING WHAT IF AN EDGE CONTAINS S AS ONE OF ITS NODES
	for edge in graph_c:
		if edge[0]==t or edge[1]==t:
			edges_t.append(edge)
	#print("time9")
	for edge in edges_t:
		edge_constraints[mapping[edge[0]][edge[1]]] = Not(edges[edge[0]][edge[1]]) # Bool(e_edge[0]_edge[1])
		edge_constraints[mapping[edge[1]][edge[0]]] = Not(edges[edge[1]][edge[0]]) # Bool(e_edge[0]_edge[1])
		removed.append(edge)
		# construct Z3 solver
		F1 = And(F,And(edge_constraints))
		s = Optimize()
		# add the formula in the solver
		s.add(F1)
		# check sat value
		result = s.check()
		if result == sat:
			break

	removed_final = []
	for edge in removed:
		edge_constraints[mapping[edge[0]][edge[1]]] = edges[edge[0]][edge[1]] # Bool(e_edge[0]_edge[1])
		edge_constraints[mapping[edge[1]][edge[0]]] = edges[edge[1]][edge[0]] # Bool(e_edge[0]_edge[1])
		
		F1 = And(F,And(edge_constraints))
		s = Solver()
		# add the formula in the solver
		s.add(F1)
		# check sat value
		result = s.check()
		if result == sat:
		    # get satisfying model
		    pass
		else:
			edge_constraints[mapping[edge[0]][edge[1]]] = Not(edges[edge[0]][edge[1]]) # Bool(e_edge[0]_edge[1])
			edge_constraints[mapping[edge[1]][edge[0]]] = Not(edges[edge[1]][edge[0]]) # Bool(e_edge[0]_edge[1])
			#print("unsat")
			removed_final.append(edge)

	return len(removed_final)



