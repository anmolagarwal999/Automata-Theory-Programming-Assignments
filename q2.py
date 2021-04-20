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

EPSILON_CHAR='$'
#########################################################################
input_nfa=None
print("Investigating input NFA")
# read file
with open(INPUT_FILE_NAME, 'r') as fd:
    input_nfa=json.load(fd)


# print(type(input_nfa))
# print(input_nfa)

# print("KEYS in input nfa ARE ")
# for k in input_nfa:
#     print(k)
# print("Input NFA investigation done")

STATES_IN_NFA=input_nfa['states']
# NUM_STATES_IN_NFA=len(STATES_IN_NFA)

# NUM_STATES_IN_DFA=2**NUM_STATES_IN_NFA

dfa_obj={}

state_str_to_idx=dict()
##################################################################
# first setting total states
def populate_states(normal_set):
    print('normal set is ', *normal_set, sep='\n')
    power_set=[]
    len_normal_set=len(normal_set)

    len_power_set=2**len_normal_set
    print("tot states in dfa is ", len_power_set)
    
    for bit_num in range(0,len_power_set):
        curr_agg_state=[]
        for state_idx in range(0,len_normal_set):
            if (bit_num & (1<<state_idx))!=0:
                curr_agg_state.append(normal_set[state_idx])
        #print("elem to power seti append is ", curr_agg_state)
        power_set.append(deepcopy(curr_agg_state))
    return deepcopy(power_set)


dfa_obj["states"]=populate_states(input_nfa["states"])

print("States in DFA are ", *dfa_obj['states'],sep='\n')
part()

def get_index_of_state_in_org(the_state):
    ans=-1
    for idx, val in enumerate(input_nfa['states']):
        if val==the_state:
            ans=idx
            break

    assert(ans!=-1)
    return ans

## Map states to idx ########
for idx,state_str in enumerate(input_nfa['states']):
    state_str_to_idx[state_str]=idx

# finding final states

def get_final_states(normal_states, normal_final_states):

    # power set of final states
    power_final_set=[]

    # index of final states in original array
    final_states_idx=[]
    for lucky_state in normal_final_states:
        idx_append=state_str_to_idx[lucky_state]
        final_states_idx.append(idx_append)
    #####################################################
    curr_final_num=0
    
    for lucky_idx in final_states_idx:
        curr_final_num|=(1<<lucky_idx)
    # print("current final num representing bits of final is ", curr_final_num)
    # print("[BINARY ]current final num representing bits of final is ", "{0:b}".format(curr_final_num))
    ########################################################
    len_normal_set=len(normal_states)

    len_power_set=2**len_normal_set
    # print("tot states in dfa is ", len_power_set)
    
    for bit_num in range(0,len_power_set):
        
        # bit_num has atleast one accept state
        if (bit_num & curr_final_num)!=0:
            curr_agg_state=[]
            for state_idx in range(0,len_normal_set):
                if (bit_num & (1<<state_idx))!=0:
                    curr_agg_state.append(normal_states[state_idx])
            power_final_set.append(curr_agg_state)
        
    return deepcopy(power_final_set)
        




dfa_obj['final_states']=get_final_states(input_nfa['states'], input_nfa['final_states'])

# print("Final States in DFA are ", *dfa_obj['final_states'],sep='\n')
# part()
# print("#############################################################")
dfa_obj['letters']=deepcopy(input_nfa['letters'])

epsilon_closure_dict=dict()

#############################
# setup edges for dfs
eps_edges=dict()

def cal_epsilon_edges(normal_states, edge_list):

    ans_eps_edges=dict()

    # Init with empty array
    for a_state in normal_states:
        ans_eps_edges[a_state]=[]
    
    for eps_edge in edge_list:
        src,wt, dest=deepcopy(eps_edge)
        # print(f"src is ", src)
        # print(f"dest is ", dest)
        # print(f"wt is ", wt)
        if wt==EPSILON_CHAR:
            ans_eps_edges[src].append(dest)

    for a_state in normal_states:
        ans_eps_edges[a_state]=list(set(ans_eps_edges[a_state]))

    return ans_eps_edges       


eps_edges=cal_epsilon_edges(input_nfa['states'], input_nfa['transition_matrix'])
# print("EPS EDGES IS ", eps_edges)
part()
print (json.dumps(eps_edges, indent=2))
part()
part()
###########################


# Calculate eps closure for each vertex

def dfs_eps(s, vis_arr):
    if vis_arr[s]==False:
        vis_arr[s]=True
        for x in eps_edges[s]:
            dfs_eps(x, vis_arr)

def calculate_eps_closure_each(normal_states, eps_edges):

    def_visit_arr={}
    for i in normal_states:
        def_visit_arr[i]=False

    tmp_eps_closure_tracker=dict()

    for curr_state in normal_states:

        # init visited array
        curr_vis_arr=deepcopy(def_visit_arr)

        dfs_eps(curr_state, curr_vis_arr)

        tmp_eps_closure_tracker[curr_state]=[]

        for tmp_state in normal_states:
            if curr_vis_arr[tmp_state]:
                tmp_eps_closure_tracker[curr_state].append(tmp_state)

    return tmp_eps_closure_tracker

eps_closure_tracker=calculate_eps_closure_each(input_nfa['states'], deepcopy(eps_edges))

print("EPS CLOSURE TRACKER IS ")
print (json.dumps(eps_closure_tracker, indent=2))


'''CALCULATE START STATE USING EPSILON CLOSURE'''

def get_epsiloned_start_states(normal_start_states):
    dfa_start_states=[]

    # NFA may have several start states as per Moodle
    for a_state in normal_start_states:
        dfa_start_states.extend(deepcopy(eps_closure_tracker[a_state]))

    # Keeping inly unique members
    dfa_start_states=list(set(dfa_start_states))
    return dfa_start_states

dfa_obj['start_states']=[get_epsiloned_start_states(deepcopy(input_nfa['start_states']))]

print("STart state of dfa is ", dfa_obj['start_states'])
part()

    
# Transition function

def get_dfa_transition(dfa_states, alphabet, nfa_trans):

    dfa_states=deepcopy(dfa_states)
    dfa_trans_list=[]
    
    for curr_dfa_state in dfa_states:

        for curr_ch in alphabet:

            trans_obj=[]
            dest_dfa_state=[]

            # -----------------------------------------zz

            for curr_edge in nfa_trans:
                src,wt, dest=deepcopy(curr_edge)
                # this edge will be usful
                # for this source, there exists some destination;
                # I can visit this destination + eps closure of this destination
                if wt==curr_ch and (src in curr_dfa_state):
                    dest_dfa_state.extend(deepcopy(eps_closure_tracker[dest]))

            # keep unique states only
            dest_dfa_state=list(set(dest_dfa_state))
            dest_dfa_state.sort()
            # -----------------------------------------

            trans_obj=[deepcopy(curr_dfa_state),curr_ch, deepcopy(dest_dfa_state)]
            dfa_trans_list.append(deepcopy(trans_obj))
    
    return dfa_trans_list

dfa_obj['transition_matrix']=get_dfa_transition(dfa_obj['states'], dfa_obj['letters'], input_nfa['transition_matrix'])
# print("Transition function is for NFA ")

# print(*dfa_obj['transition_matrix'], sep='\n')


part()
part()
print(dfa_obj)

with open(OUTPUT_FILE_NAME, "w") as outfile:
    json.dump(dfa_obj, outfile)


            








