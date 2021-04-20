import os
import sys
from copy import deepcopy
import json
# from graphviz import Digraph

# total arguments
n_args = len(sys.argv)
print("Total arguments passed:", n_args)

if n_args<2:
    print("ERROR: Seems like no regex string was passed")
    sys.exit()

INPUT_FILE_NAME=sys.argv[1]
OUTPUT_FILE_NAME=sys.argv[2]
#######################################################

def part():
    print("---------------------------------------")


input_dfa = None
# read file
with open(INPUT_FILE_NAME, 'r') as fd:
    input_dfa = json.load(fd)

    # DFA:
    # {
    #     "states": [<array_of_all_states>],
    #     "letters": [<array_of_letters>],
    #     "transition_function": [
    #                             [<original_state>, <input_letter>, <new_state>],
    #                             [<original_state>, <input_letter>, <new_state>],
    #                             .
    #                             .
    #                             .

    #                         ],
    #     "start_states": [<array_of_start_states>],
    #     "final_states": [<array_of_final_states>],
    # }
CURR_GLOBAL_COUNTER=0


#############################
# enumming operators
STAR_OP = '*'
PLUS_OP = '+'
CONCAT_OP = '.'

# Brackets
OPENING_BRACKET = '('
CLOSING_BRACKET = ')'

EPSILON_CHAR = '$'
# UNION and CONCAT (STAR NOT INCLUDED HERE)
SIMPLE_OPERATORS = [PLUS_OP, CONCAT_OP]
##################################
GLOBAL_STATE_COUNTER=len(input_dfa['states'])
OLD_TRANS_FUNC=deepcopy(input_dfa['transition_matrix'])
################################
# Enclose all existing in bracket
# Group those with OR where same <src, dest>
# Add new start state and end state
# Remove now
########################################

def get_new_state():
    global GLOBAL_STATE_COUNTER
    GLOBAL_STATE_COUNTER+=1
    state_num=GLOBAL_STATE_COUNTER
    return state_num

MASTER_START_STATE='Q'+str(get_new_state())
MASTER_ACCEPT_STATE='Q'+str(get_new_state())


# append new states
input_dfa['states'].append(MASTER_ACCEPT_STATE)
input_dfa['states'].append(MASTER_START_STATE)

# Enclose all transitions in brackets

# for edge in input_dfa['transition_matrix']:
#     # edge[1]='('+edge[1]+')'
#     edge[1]=edge[1]

def convert_to_GNFA():
    adj_matrix=dict()
    
    for curr_edge in input_dfa['transition_matrix']:
        src, wt, dest=curr_edge
        ref_tuple=(src, dest)
        if ref_tuple in adj_matrix:
            adj_matrix[ref_tuple]+=PLUS_OP+wt
        else:
            adj_matrix[ref_tuple]=wt
    new_trans_func=[]

    for key, val in adj_matrix.items():
        val_append=val
        # if not (val[0]=='(' and val[-1]==')'):
        #     val_append='('+val_append+')'

        new_trans_func.append([ key[0]   ,'('+val_append+')'  , key[1]  ])

    return new_trans_func
    
        
mod_trans_func=convert_to_GNFA()

input_dfa['transition_matrix']=deepcopy(mod_trans_func)

# Add eps from curr start edge to existing edges
for a_state in input_dfa['start_states']:
    # input_dfa['transition_matrix'].append([MASTER_START_STATE, '('+EPSILON_CHAR+')', a_state])
    input_dfa['transition_matrix'].append([MASTER_START_STATE, EPSILON_CHAR, a_state])

    # Add eps from curr start edge to existing edges
for a_state in input_dfa['final_states']:
    input_dfa['transition_matrix'].append([a_state,EPSILON_CHAR, MASTER_ACCEPT_STATE])


print(*input_dfa['transition_matrix'],sep='\n')

# part()


# print("OLD trans func is ", *OLD_TRANS_FUNC, sep='\n')
# part()
# print("MOD trans func is ", *mod_trans_func, sep='\n')

tinker_trans_func=dict()
for curr_edge in input_dfa['transition_matrix']:
    tinker_trans_func[(curr_edge[0], curr_edge[2])]=curr_edge[1]

print("tinker func is ", tinker_trans_func)

curr_states_list=deepcopy(input_dfa['states'])

while(len(curr_states_list)>2):

    # decide a state to penalize
    rem_state=None
    for a_state in curr_states_list:
        if a_state==MASTER_ACCEPT_STATE or a_state==MASTER_START_STATE:
            continue
        rem_state=a_state
        break
    assert(rem_state!=None)

    for curr_src in curr_states_list:
        if curr_src==rem_state:
            continue

        for curr_dest in curr_states_list:
            if curr_dest==rem_state:
                continue

            # There must be an edge from `src to rem` and `rem to dest`
            if ((curr_src, rem_state) not in tinker_trans_func) or ((rem_state, curr_dest) not in tinker_trans_func):
                continue

            R=None
            R1=tinker_trans_func[(curr_src, rem_state)]
            R2=None
            R3=tinker_trans_func[(rem_state, curr_dest)]

            new_src_to_dest=""
            if (curr_src, curr_dest) in tinker_trans_func:
                R=tinker_trans_func[(curr_src,curr_dest)]
            
            if (rem_state, rem_state) in tinker_trans_func:
                R2=tinker_trans_func[(rem_state, rem_state)]
        
            if R is not None:
                new_src_to_dest=R+PLUS_OP
            
            if R2 is None:
                new_src_to_dest+=R1+R3
            else:
                new_src_to_dest+=R1+R2+"*"+R3
            new_src_to_dest="("+new_src_to_dest+")"

            tinker_trans_func[(curr_src, curr_dest)]=new_src_to_dest
    
    # Delete all evidence of rem state in transition function
    del_keys=[]
    for key, val in tinker_trans_func.items():
        if key[0]==rem_state or key[1]==rem_state:
            del_keys.append(key)
    for unlucky_key in del_keys:
        del tinker_trans_func[unlucky_key]
    curr_states_list.remove(rem_state)

print("FInal trans is ", tinker_trans_func)
# assert(len(tinker_trans_func)>1)
ans_reg=dict()
assert(len(tinker_trans_func.keys())==1)
for key in tinker_trans_func.keys():
    print("key is ", key)
    val=tinker_trans_func[key]
    print("val is ", val)
    ans_reg['regex']=val

with open(OUTPUT_FILE_NAME, "w") as outfile:
    json.dump(ans_reg, outfile)






