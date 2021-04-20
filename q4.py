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
CURR_GLOBAL_COUNTER = 0

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
GLOBAL_STATE_COUNTER = len(input_dfa['states'])
OLD_TRANS_FUNC = deepcopy(input_dfa['transition_matrix'])
################################
# Enclose all existing in bracket
# Group those with OR where same <src, dest>
# Add new start state and end state
# Remove now
########################################

# Minimized DFA
'''
1) STates => vary
2) letter=> same
3) start state => vary
4) Final states: wherever a final state is present
5) Transition => from parents
'''
'''FIRST REMOVE UNREACHABLE states USING THIS ONLY, remove unreachable state from final state and transition'''

old_dfa_start_state = input_dfa["start_states"][0]

assert (len(input_dfa["start_states"]) == 1)
########################################################
visit_arr = dict()
for a_state in input_dfa['states']:
    visit_arr[a_state] = False

#print(visit_arr)

def dfs_check(s):
    if visit_arr[s] == False:
        visit_arr[s] = True

        for curr_edge in input_dfa['transition_matrix']:
            src, wt, dest = curr_edge
            if src == s:
                dfs_check(dest)


dfs_check(old_dfa_start_state)

print("Visit updated is ", visit_arr)


mid_dfa = deepcopy(input_dfa)

# Removing unvisited from `states` AND `final_states`
for i in range(0, len(input_dfa['states'])):
    if visit_arr[input_dfa['states'][i]] == False:
        # Remove state
        mid_dfa['states'].remove(input_dfa['states'][i])

        if input_dfa['states'][i] in mid_dfa['final_states']:
            mid_dfa['final_states'].remove(input_dfa['states'][i])

# Keeping only those transitions which are not in removed folks
mid_dfa['transition_matrix'] = []

for curr_edge in input_dfa['transition_matrix']:
    src, wt, dest = curr_edge
    if (src in mid_dfa['states']) and (dest in mid_dfa['states']):
        mid_dfa['transition_matrix'].append(deepcopy(curr_edge))
#########################################################################
# Initially, all nC2 nodes are unmarked
marking_details = dict()
for node_1 in mid_dfa['states']:
    for node_2 in mid_dfa['states']:
        marking_details[(node_1, node_2)] = False


def mark_pair(n1, n2):
    marking_details[(n1, n2)] = True
    marking_details[(n2, n1)] = True


def is_marked(n1, n2):
    assert (marking_details[(n1, n2)] == marking_details[(n2, n1)])
    return marking_details[(n1, n2)]


#####################################
# Now, mark accept and non-accept as marked
for final_state in mid_dfa['final_states']:
    for a_state in mid_dfa['states']:
        if a_state not in mid_dfa['final_states']:
            # Mark
            mark_pair(final_state, a_state)

# Now, till no more changes possible, keep marking
trans_master = dict()

for curr_edge in mid_dfa['transition_matrix']:
    src, wt, dest = curr_edge
    trans_master[(src, wt)] = dest

print("trans master is ", trans_master)
while True:
    num_new_markings = 0

    for n1 in mid_dfa['states']:
        for n2 in mid_dfa['states']:
            # check if still unmarked
            if is_marked(n1, n2) == False:
                # check if they should be marked

                for curr_ch in input_dfa['letters']:
                    end_1 = trans_master[(n1, curr_ch)]
                    end_2 = trans_master[(n2, curr_ch)]
                    if is_marked(end_1, end_2):
                        mark_pair(n1, n2)
                        num_new_markings += 1
                        break

    if num_new_markings == 0:
        break

# all marked stuff done
new_states_arr = []
allotted_state_idx = dict()

for curr_state in mid_dfa['states']:
    allotted_state_idx[curr_state] = -1

curr_idx = -1

for curr_state in mid_dfa['states']:
    print('curr state is ', curr_state)
    print("allotted to it is ", allotted_state_idx[curr_state])
    if allotted_state_idx[curr_state] == -1:
        curr_idx += 1
        new_state_here = [curr_state]
        allotted_state_idx[curr_state] = curr_idx
        for other_state in mid_dfa['states']:
            if curr_state == other_state:
                continue
            if is_marked(curr_state, other_state) is False:
                allotted_state_idx[other_state] = curr_idx
                new_state_here.append(other_state)
        new_state_here = list(set(new_state_here))
        new_states_arr.append(deepcopy(new_state_here))

part()
part()
ans_obj = dict()
print("Newly grouped states are ")
print(*new_states_arr)
ans_obj['states'] = new_states_arr

# decide final state
final_states_chunks_idx = []
for lucky_state in mid_dfa['final_states']:
    final_states_chunks_idx.append(allotted_state_idx[lucky_state])

# making sure that duplicated do not arise
final_states_chunks_idx = list(set(final_states_chunks_idx))
ans_obj['final_states'] = []
for idx in final_states_chunks_idx:
    ans_obj['final_states'].append(deepcopy(new_states_arr[idx]))

# find where the start state is
ans_obj['start_states']=deepcopy(new_states_arr[allotted_state_idx[old_dfa_start_state]])

# change transition function
already_in_transition=[]
ans_obj['transition_matrix'] = []
for edge in mid_dfa['transition_matrix']:
    src, wt, dest = edge
    if (allotted_state_idx[src],wt,allotted_state_idx[dest]) not in already_in_transition:
        new_element = [
            new_states_arr[allotted_state_idx[src]],\
            wt,
            new_states_arr[allotted_state_idx[dest]]
        ]
        ans_obj['transition_matrix'].append(new_element)
        already_in_transition.append((allotted_state_idx[src],wt,allotted_state_idx[dest]))

# letters
ans_obj['letters']=input_dfa['letters']


with open(OUTPUT_FILE_NAME, "w") as outfile:
    json.dump(ans_obj, outfile)   


