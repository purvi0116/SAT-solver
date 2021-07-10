from z3 import *
import numpy as np
import random

def choose_iter(elements, length):
    for i in range(len(elements)):
        if length == 1:
            yield (elements[i],)
        else:
            for next in choose_iter(elements[i+1:len(elements)], length-1):
                yield (elements[i],) + next
def choose(l, k):
    return list(choose_iter(l, k))


def initialize(n, k) :
	print("n: ",n ,"k: ", k )
	global tried
	tried = 0
	global count
	count = 1
	global num_colors
	num_colors = n
	global freq
	freq = [0]*num_colors
	global length
	length = k
	global s
	s = Solver()
	for i in range(length) :
		s.add(PbEq( [( Bool("p_{a}_{b}".format(a=j, b=i)), 1 ) for j in range(num_colors)], 1)) #each place exactly one color
	

def get_second_player_move() :
	
	global output
	output = []
	global tried
	global count
	global prev_output
	global s

	count = 1 - count
	
	if count==0 :
		if tried<num_colors:
			output = [tried]*length
			tried+=1
		
		elif s.check()==sat :
			m = s.model()
			for i in range(length) :
				for j in range(num_colors) :
					var = Bool("p_{a}_{b}".format(a=j, b=i))
					if m[var] :
						output.append(j) 
						break

		else : # conflicting feedback
			s = Solver()
			for i in range(length) :
				s.add(PbEq( [( Bool("p_{a}_{b}".format(a=j, b=i)), 1 ) for j in range(num_colors)], 1)) #each place exactly one color
			output = [0]*length

	else :
		output = prev_output
		
	prev_output = output
	return output

def put_first_player_response(red, white) :
	global freq
	global tried
	global prev_response
	global count
	global s

	if count==0 : prev_response = (red, white)

	elif prev_response==(red, white) :
		if tried<=num_colors:
			freq[tried-1] = red+white
			s.add(PbEq([( Bool("p_{a}_{b}".format(a=tried-1,b=pos)) ,1) for pos in range(length)],freq[tried-1]))
			if tried==num_colors:
				tried=2*num_colors
			return 

		s.add( PbEq( [ (Bool( "p_{a}_{b}".format(a=output[i], b=i) ), 1) for i in range(length)], red)) # exactly #red values in output are correct
		return 
	