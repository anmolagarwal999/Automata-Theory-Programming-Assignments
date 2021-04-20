import os
import sys
from copy import deepcopy
import json
from graphviz import Digraph



def part():
    print("---------------------------------------")
 
# total arguments
n = len(sys.argv)
print("Total arguments passed:", n)

if n<2:
    print("ERROR: Seems like no regex string was passed")
    sys.exit()
 
# Arguments passed
# print("\nName of Python script:", sys.argv[0])
 
print("\nArguments passed:", end = " ")
for i in range(1, n):
    print(f'arg {i} is ',sys.argv[i], end = "\n")

print("Arguments checked")
part()


# REGEX_INPUT = sys.argv[1]
REGEX_INPUT_FILE=sys.argv[1]
REGEX_INPUT=None
with open(REGEX_INPUT_FILE,'r') as f:    
    data_tmp = json.load(f)
    REGEX_INPUT=data_tmp['regex']

# REGEX_INPUT=sys.argv[1]

OUTPUT_FILE_FROM_TERMINAL=sys.argv[2]
print(f"output file is {OUTPUT_FILE_FROM_TERMINAL}")
REGEX_INPUT_BACKUP=deepcopy(REGEX_INPUT)
#############################
# enumming operators
STAR_OP = '*'
PLUS_OP = '+'
CONCAT_OP = '.'

# Brackets
OPENING_BRACKET = '('
CLOSING_BRACKET = ')'

LETTERS_ENCOUNTERED=[]


# UNION and CONCAT (STAR NOT INCLUDED HERE)
SIMPLE_OPERATORS = [PLUS_OP, CONCAT_OP]

# Defining alphabet
'''MOODLE:  Input alphabet can consist of any digits or English letters ("a-z0-9") as that is the convention followed in most literature.'''
LOWERCASE = [chr(i) for i in range(97, 123)]
# UPPERCASE = [chr(i) for i in range(65, 91)]
NUMERIC = [chr(i) for i in range(48, 58)]
EPSILON='$'


# ALPHABET = [EPSILON,*LOWERCASE, *UPPERCASE, *NUMERIC]
ALPHABET = [EPSILON,*LOWERCASE, *NUMERIC]
print(f'Alphabet is \n')
print(*ALPHABET, sep=' | ')


def make_regex_meet_standards(tmp_regex):
    '''STILL IMPLEMENTATION LEFT TO COMPREHENSIVELY CHECK VALIDITY of REGEX'''
    print(f"Regex we want to make meet standards is {tmp_regex}")
    ideal_regex = ""
    prev_ch = None
    for curr_ch in tmp_regex:

        if curr_ch in ALPHABET:
            '''
                Prev can either be 
                1) Concat (.)
                2) Union (+)
                3) Star
                4) Opening brack
                5) CLose brack
                6) An alphabet

                Add dot manually only if previous was not a dot and (previos was a alphabet or a closing bracket or STAR)
                '''
            if prev_ch in [CLOSING_BRACKET, *ALPHABET, STAR_OP
                           ] and prev_ch != CONCAT_OP:
                '''Cases like [aa],    [)a],  [*a]  '''
                ideal_regex += CONCAT_OP

        elif curr_ch == OPENING_BRACKET:
            '''
                Prev can either be 
                1) Concat (.)
                2) Union (+)
                3) Star
                4) Opening brack
                5) CLose brack
                6) An alphabet

                Add dot manually only if previous was not a dot and (previos was a alphabet or a closing bracket or STAR)
                '''
            if prev_ch in [CLOSING_BRACKET, *ALPHABET, STAR_OP
                           ] and prev_ch != CONCAT_OP:
                '''Cases like [a(],    [)(],  [*(]  '''
                ideal_regex += CONCAT_OP

        elif curr_ch == CLOSING_BRACKET:
            '''PREV CANNOT BE PLUS or CONCAT
            
            Prev can either be 
               
                Star
                Opening brack
                CLose brack
                An alphabet
                '''
            if prev_ch in [PLUS_OP, CONCAT_OP]:
                raise Exception(
                    "PREV CANNOT BE PLUS or CONCAT before CLOSING BRACKET")

        elif curr_ch in SIMPLE_OPERATORS:
            # plus or concat
            '''SIMPLE OP before SIMPLE op and opening brck before simple op not allowed'''
            if prev_ch in [*SIMPLE_OPERATORS, OPENING_BRACKET]:
                raise Exception(
                    "SIMPLE OP before SIMPLE op and opening brck before simple op not allowed"
                )

        elif curr_ch == STAR_OP:
            # If kleene star
            '''
            PREV CAN BE
            5) CLose brack
            6) An alphabet
            '''

            if prev_ch not in [CLOSING_BRACKET, *ALPHABET]:
                raise Exception(
                    "before KLEENE STAR,  PREV CAN BE 5) CLose brack 6) An alphabet"
                )

        else:
            print("Invalid ch is ", curr_ch)
            raise Exception(f"Character -> {curr_ch}  -> seems to be invalid")

        # Add char to ideal_regex

        ideal_regex += curr_ch
        prev_ch = curr_ch
    return ideal_regex

######################################################################

# use_regex = make_regex_meet_standards(REGEX_INPUT)

# for idx, sample_regex in enumerate(TEST_INPUTS):
#     use_regex = make_regex_meet_standards(sample_regex)
#     print(f'{sample_regex} ----->  {use_regex}')
#     TEST_INPUTS[idx]=use_regex
#     part()
#     # break

REGEX_INPUT=make_regex_meet_standards(REGEX_INPUT_BACKUP)

###############################################
GLOBAL_STATE_COUNTER=0

def get_new_state():
    global GLOBAL_STATE_COUNTER
    GLOBAL_STATE_COUNTER+=1
    state_num=GLOBAL_STATE_COUNTER
    return state_num

class base_NFA:
    def __init__(self, character_used=None,find_new_start=False):
        #print("initing base NFA")
        if find_new_start==False:
            self.start_node = None
            self.accept_node=None
        else:
            self.start_node = get_new_state()
            self.accept_node = get_new_state()
        
        transition_default={
            "start_node":self.start_node,
            "accept_node":self.accept_node,
            'edge_char':character_used
        }

        # Initialy, this NFA has just one edge
        self.edges=[transition_default]

##########################################################



CHARACTER_STACK=[]
JUNIOR_NFAS=[]

def apply_union(nfa_1, nfa_2):
    
    # if isinstance(nfa_1,base_NFA)!=False or isinstance(nfa_2,base_NFA)!=False:
    #     # part()
    #     # print("t is ", type(nfa_1))
    #     # raise TypeError("Class mismatch. Goliath Errors")
    #     pass

    # # s1, q1
    # # s2, q2

    s1=nfa_1.start_node
    q1=nfa_1.accept_node

    s2=nfa_2.start_node
    q2=nfa_2.accept_node

    assert(s1!=None)
    assert(s2!=None)
    assert(q1!=None)
    assert(q2!=None)



    # new => s0, q0
    new_start=get_new_state()
    new_accept=get_new_state()

    ans_nfa=base_NFA(find_new_start=False)

    ans_nfa.start_node=new_start
    ans_nfa.accept_node=new_accept 

    # all original edges + epsilon edges from s0  -> s1, s2 and q1, q2 => q0

    NEWLY_ADDED_EDGES=[


        {
            "start_node":new_start,
            "accept_node":s1,
            'edge_char':EPSILON
        },

        {
            "start_node":new_start,
            "accept_node":s2,
            'edge_char':EPSILON
        },

        {
            "start_node":q1,
            "accept_node":new_accept,
            'edge_char':EPSILON
        },

        {
            "start_node":q2,
            "accept_node":new_accept,
            'edge_char':EPSILON
        }
    ]

    new_edge_list=[*deepcopy(nfa_1.edges), *deepcopy(nfa_2.edges),*NEWLY_ADDED_EDGES]
    ans_nfa.edges=new_edge_list   

    return ans_nfa

    

def apply_concatenation(nfa_1, nfa_2):
    # if isinstance(nfa_1,base_NFA)!=False or isinstance(nfa_2,base_NFA)!=False:
    #     # part()
    #     # print("t is ", type(nfa_1))
    #     # raise TypeError("Class mismatch. Exodus Errors")
    #     pass

    # s1, q1
    # s2, q2

    s1=nfa_1.start_node
    q1=nfa_1.accept_node

    s2=nfa_2.start_node
    q2=nfa_2.accept_node
    assert(s1!=None)
    assert(s2!=None)
    assert(q1!=None)
    assert(q2!=None)

    ans_nfa=base_NFA(find_new_start=False)

    ans_nfa.start_node=s1
    ans_nfa.accept_node=q2

    # all original edges + epsilon edges from q1 => s2

    NEWLY_ADDED_EDGES=[
        {
            "start_node":q1,
            "accept_node":s2,
            'edge_char':EPSILON
        }
    ]

    # Add existing edges of children NFAs
    new_edge_list=[*deepcopy(nfa_1.edges), *deepcopy(nfa_2.edges),*NEWLY_ADDED_EDGES]
    ans_nfa.edges=new_edge_list
    return ans_nfa


def apply_kleene_star(curr_nfa):

    # s1, q1
    s1=curr_nfa.start_node
    q1=curr_nfa.accept_node

    assert(s1!=None)
    assert(q1!=None)

    # new => s0, q0
    new_start=get_new_state()
    new_accept=get_new_state()

    ans_nfa=base_NFA(find_new_start=False)
    ans_nfa.start_node=new_start
    ans_nfa.accept_node=new_accept

    # all original edges + epsilon edges from 
    # 1) s0=>s1
    # 2) s1=>q0 (MUST, AS EMPTY STRING needs to be accepted as well)
    # 3) q1 => s1
    # [just q1=>q0 WON'T BE SUFFICIENT due to the empty string case]

    # THeorem 1.49
    NEWLY_ADDED_EDGES=[
        {
            "start_node":new_start,
            "accept_node":s1,
            'edge_char':EPSILON
        },

        # # One (slightly bad) idea is simply to add the start state to the set of accept states.
        # {
        #     "start_node":s1,
        #     "accept_node":new_accept,
        #     'edge_char':EPSILON
        # },

        {
            "start_node":q1,
            "accept_node":s1,
            # "accept_node":new_start,
            'edge_char':EPSILON
        },
          {
            "start_node":new_start,
            "accept_node":new_accept,
            'edge_char':EPSILON
        },
          {
            "start_node":q1,
            "accept_node":new_accept,
            'edge_char':EPSILON
        }
    ]

    new_edge_list=[*deepcopy(curr_nfa.edges), *NEWLY_ADDED_EDGES]
    ans_nfa.edges=new_edge_list
    return ans_nfa

    



def apply_operator(curr_op):

    # print("Trying to apply operator ", curr_op)
    if curr_op in SIMPLE_OPERATORS:
        # Either CONCAT OR UNION
        
        assert(len(JUNIOR_NFAS)>=2)

        # the latest NFA would be popped first (take care)
        nfa_2=JUNIOR_NFAS.pop()
        nfa_1=JUNIOR_NFAS.pop()

        if curr_op==PLUS_OP:
            res_nfa=apply_union(nfa_1, nfa_2)
        else:
            res_nfa=apply_concatenation(nfa_1, nfa_2)

        JUNIOR_NFAS.append(res_nfa)
    
    elif curr_op==STAR_OP:

        assert(len(JUNIOR_NFAS)>0)
        lucky_nfa=JUNIOR_NFAS.pop()
        res_nfa=apply_kleene_star(lucky_nfa)
        JUNIOR_NFAS.append(res_nfa)

    else:
        raise Exception("Is not a valid operator")

def check_precedence_and_apply(curr_op):
    if curr_op==STAR_OP:
        # apply with no questions asked
        apply_operator(curr_op)
    else:
        while(True):
            if len(CHARACTER_STACK)==0:
                # First entry
                break
            elif CHARACTER_STACK[-1]==OPENING_BRACKET:
                # Can't empty stack as there is a chance that KLEENE STAR MIGHT COME LATER
                # Avoid error in a tc like `a+(bcd+e)*`
                break
            else:
                # Now, if currently . and I am exploring . => can do (without involving current operator)
                # Now, if currently . and I am exploring + => CANNOT do take case of A+B.C.D
                # Now, if currently + and I am exploring + => can do (without involving current operator)
                # Now, if currently + and I am exploring . => can do (without involving current operator)
                if CHARACTER_STACK[-1]==curr_op or CHARACTER_STACK[-1]==CONCAT_OP:
                    apply_operator(CHARACTER_STACK.pop())
                else:
                    break
        CHARACTER_STACK.append(curr_op)
        


def get_NFA_for_regex(master_regex):

    '''STILL IMPLEMENTATION LEFT TO COMPREHENSIVELY CHECK VALIDITY of REGEX'''
    print(f"Input for conversion procudre is ->     {master_regex}")
    #ideal_regex = ""
    prev_ch = None
    for curr_ch in master_regex:

        ####################################################################
        '''
        Alphabet => make trivial_NFA and push on list,
        if kleene => taken care at the bottom
        if +/. => taken care at bottom       
        
        '''
        if curr_ch in ALPHABET:
          
            if prev_ch in [CLOSING_BRACKET, *ALPHABET, STAR_OP
                           ] and prev_ch != CONCAT_OP:
                '''Cases like [aa],    [)a],  [*a]  '''
                raise Exception ("WEIRD STUFF")

            #------------------------------------------
            # CHARACTER_STACK.append(curr_ch)s
            nfa_to_append=base_NFA(character_used=curr_ch, find_new_start=True)
            LETTERS_ENCOUNTERED.append(curr_ch)
            # print(f'---- NFA append class is {type(nfa_to_append)}')
            JUNIOR_NFAS.append(nfa_to_append)
        ####################################################################

        elif curr_ch == OPENING_BRACKET:
            '''
            Add opening bracket as plcaeholder to track component            
            '''
            
            if prev_ch in [CLOSING_BRACKET, *ALPHABET, STAR_OP
                           ] and prev_ch != CONCAT_OP:
                '''Cases like [a(],    [)(],  [*(]  '''
                raise Exception ("WEIRD STUFF")

            # Append to stack to mark SPOT till where processing needs to be done before KLEENE is applied

            CHARACTER_STACK.append(curr_ch)

            

        ####################################################################

        elif curr_ch == CLOSING_BRACKET:
            '''PREV CANNOT BE PLUS or CONCAT'''
            if prev_ch in [PLUS_OP, CONCAT_OP]:
                raise Exception(
                    "PREV CANNOT BE PLUS or CONCAT before CLOSING BRACKET")

            while (len(CHARACTER_STACK)>0 and CHARACTER_STACK[-1]!=OPENING_BRACKET):
                # char popped wil either be OPENING_BRACKET in which loop would not have reached here in the first place
                # Hence, it can be an operator only
                char_popped=CHARACTER_STACK.pop()
                apply_operator(char_popped)

            # Closing bracket must have opening bracket counterpart
            assert(CHARACTER_STACK[-1]==OPENING_BRACKET)
            CHARACTER_STACK.pop()
        ####################################################################

        elif curr_ch in SIMPLE_OPERATORS:
            # plus or concat
            '''SIMPLE OP before SIMPLE op and opening brck before simple op not allowed'''
            if prev_ch in [*SIMPLE_OPERATORS, OPENING_BRACKET]:
                raise Exception(
                    "SIMPLE OP before SIMPLE op and opening brck before simple op not allowed"
                )
            check_precedence_and_apply(curr_ch)
            
        ####################################################################

        elif curr_ch == STAR_OP:
            # If kleene star
            '''
            PREV CAN BE
            5) CLose brack
            6) An alphabet
            '''

            if prev_ch not in [CLOSING_BRACKET, *ALPHABET]:
                raise Exception(
                    "before KLEENE STAR,  PREV CAN BE 5) CLose brack 6) An alphabet"
                )
            check_precedence_and_apply(curr_ch)
            
        ####################################################################

        else:
            print("Invalid ch is ", curr_ch)
            raise Exception(f"Character -> {curr_ch}  -> seems to be invalid")
        
        prev_ch = curr_ch

    #######################################################################
    # Now, empty stack as danger of KLEENE operator coming is no longer there

    ####################################################################
    
    # print(f"Before final journey, CHAR STACK IS {CHARACTER_STACK}")

    while (len(CHARACTER_STACK)) != 0:

        'PRECEDENCE HANDLING ???'
        op = CHARACTER_STACK.pop()
        apply_operator(op)
    if len(JUNIOR_NFAS) > 1:
        print(f'NFAs have not been reduced (ERROR) is {JUNIOR_NFAS}')
        raise (Exception("Regex could not be parsed successfully"))
    #print(f"Success NFA is {JUNIOR_NFAS[-1].__dict__}")
    ret_nfa=JUNIOR_NFAS[-1]
    return ret_nfa

    
part()
part()
part()
part()
print("Starting coversion procedure")
final_nfa=get_NFA_for_regex(REGEX_INPUT)
print("Coversion procedure ENDED")


# print (json.dumps(final_nfa.__dict__, indent=2))

print("Now converting to ANS NFA")



def convert_to_submission_format():
    ans_obj=dict()
  
    ans_obj['letters']=list(set([*LETTERS_ENCOUNTERED, EPSILON]))

    def get_state_str(num):
        return "Q"+str(num)

    num_states_used=GLOBAL_STATE_COUNTER+1

    curr_states_list=[]

    for i in range(1,num_states_used):
        curr_states_list.append(get_state_str(i))

    ans_obj['states']=curr_states_list
    ans_obj['start_states']=[get_state_str(final_nfa.start_node)]
    ans_obj['final_states']=[get_state_str(final_nfa.accept_node)]

    delta_list=[]
    for i in final_nfa.edges:
        tmp_obj=[get_state_str(i['start_node']), i['edge_char'], get_state_str(i['accept_node'])]
        delta_list.append(deepcopy(tmp_obj))
    ans_obj['transition_function']=delta_list
    return ans_obj
    
ans_nfa=convert_to_submission_format()

part()
part()
print (json.dumps(ans_nfa, indent=2))



# https://graphviz.readthedocs.io/en/stable/examples.html#fsm-py
def show_visual(curr_nfa):

    f = Digraph()
    f.attr(rankdir='LR', size='8,5')

    f.attr('node', shape='doublecircle')
    f.node(curr_nfa['final_states'][0])
    

    f.attr('node', shape='circle')
    for i in curr_nfa['transition_function']:
        f.edge(i[0], i[2], label=i[1])
        
    # f.view()
    f.attr(label=REGEX_INPUT_BACKUP)
    f.render(filename=f'pdf_version.dot')

# print("keys are ", ans_nfa.keys())
# show_visual(ans_nfa)

with open(OUTPUT_FILE_FROM_TERMINAL, "w") as outfile:
    json.dump(ans_nfa, outfile)

    



