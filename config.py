
import json
import functools

class ConfigRule:
    def __init__(self, rule_func, err_str=''):
        self.rule_func = rule_func
        self.err_str = err_str
    
    def apply(self, thing):
        #print('%s    %s' % (thing, self.rule_func(thing)))
        if (self.rule_func(thing) is True):
            return (True, None)
        else:
            return (False, 'Rule violation for \'%s\': %s' % (thing,self.err_str))

isalnum  = lambda input : input.replace('_','').isalnum()
isupper  = lambda input : ((input.isupper()) and (input.replace('_','').isalnum()))
   
#rules for alias's
length_r            = ConfigRule(lambda s : (len(s)<=32), err_str='string alias is greater than 32 characters long')
int_r               = ConfigRule(lambda id : type(id)==int, err_str='id must be an integer')
constant_case_r     = ConfigRule(isupper, err_str='constant alias must only consist of uppercase alphanumeric characters and underscores')
parameter_char_r    = ConfigRule(isalnum, err_str='parameter alias must only consist of alphanumeric characters and underscores')
parameter_end_r     = ConfigRule(lambda input : input.endswith('_p'), err_str='parameter alias must end with \'_p\'')
signal_char_r       = ConfigRule(isalnum, err_str='signal alias must only consist of alphanumeric characters and underscores')
signal_end_r        = ConfigRule(lambda input : input.endswith('_s'), err_str='signal alias must end with \'_s\'')
state_machine_char_r   = ConfigRule(isalnum, err_str='state machine alias must only consist of alphanumeric characters and underscores')
state_machine_end_r    = ConfigRule(lambda input : input.endswith('_sm'), err_str='state machine alias must end with \'_sm\'')
state_char_r        = ConfigRule(isalnum, err_str='state alias must only consist of alphanumeric characters and underscores')
state_end_r         = ConfigRule(lambda input : input.endswith('_st'), err_str='state alias must end with \'_st\'')

#rules for ID's
state_machine_id_r = ConfigRule(lambda id : ((id>=0) and (id<=672)), err_str='state machine id must be in the range [0,672]')
state_id_r          = ConfigRule(lambda id : ((id>=0) and (id<=949)), err_str='state id must be in the range [0,949]')
int_r               = ConfigRule(lambda id : type(id)==int, err_str='id is not an integer')



#check if all the elements in a list only appear once
elements_unique = lambda items : (len(set(items)) == len(items))

def verify_dictionary(to_verify, key_rules, value_rules):
    err_msg = None
    all_success = True #assume all rules will pass

    for (key,val) in to_verify.items():
        for r in key_rules:
            success, err_msg = r.apply(key)
            if (success == False):
                print(err_msg)
                all_success = False
        for r in value_rules:
            success, err_msg = r.apply(val)
            if (success == False):
                print(err_msg)
                all_success = False
    
    return False if (not all_success) else True

def verify_constants(constants):
    alias_rules = [length_r, constant_case_r]
    id_rules    = [int_r]
    if not verify_dictionary(constants, alias_rules, id_rules):
        return False
    return True
    
def verify_parameters(parameters):
    alias_rules = [length_r, parameter_char_r, parameter_end_r]
    id_rules    = [int_r]
    if not verify_dictionary(parameters, alias_rules, id_rules):
        return False
    success, err_msg = ConfigRule(elements_unique, err_str='parameter id\'s must be unique').apply(parameters.values())
    if (success == False):
        print(err_msg)
        return False
    return True
    
def verify_signals(signals):
    alias_rules = [length_r, signal_char_r, signal_end_r]
    id_rules    = [int_r]
    if not verify_dictionary(signals, alias_rules, id_rules):
        return False
    success, err_msg = ConfigRule(elements_unique, err_str='signal id\'s must be unique').apply(signals.values())
    if (success == False):
        print(err_msg)
        return False
    return True
    
def verify_state_machines(state_machines,config):
    alias_rules = [length_r, state_machine_char_r, state_machine_end_r]
    id_rules    = [int_r, state_machine_id_r]
    if not verify_dictionary(state_machines, alias_rules, id_rules):
        return False
    success, err_msg = ConfigRule(elements_unique, err_str='state machine id\'s must be unique').apply(state_machines.values())
    if (success == False):
        print(err_msg)
        return False
    for entry in config:
        if (entry == 'declarations'):
            continue
        elif entry not in state_machines:
            print('state machine \'%s\' has a definition but was never declared, a state machine alias and id must be added to state machine declarations' % (entry,))
            return False
    return True
    
def verify_states(states):
    alias_rules = [length_r, state_char_r, state_end_r]
    id_rules    = [int_r, state_id_r]
    if not verify_dictionary(states, alias_rules, id_rules):
        return False
    success, err_msg = ConfigRule(elements_unique, err_str='state id\'s must be unique').apply(states.values())
    if (success == False):
        print(err_msg)
        return False
    return True
    
def check_for_required_declarations(declarations):
    required_declarations = ['constants','parameters','signals','expressions','state_machines','states']
    for r in required_declarations:
        if (r not in declarations):
            print('\'%s\' dictionary not found in declarations' % (r,))
            return False
    return True


#################################
# toplevel verification methods #
#################################

def verify_config(config):
    if ('declarations' not in config):
        print('\'declarations\' dictionary not found')
        return None
        
    declarations = config['declarations']
    if (not check_for_required_declarations(declarations)):
        return None

    constants = declarations['constants']
    parameters = declarations['parameters']
    signals = declarations['signals']
    expressions = declarations['expressions']
    state_machines = declarations['state_machines']
    states = declarations['states']
    
    if (not verify_constants(constants)):
        return None
    if (not verify_parameters(parameters)):
        return None
    if (not verify_signals(signals)):
        return None
    #if (not verify_expressions(expressions)):
    #    return None
    if (not verify_state_machines(state_machines,config)):
        return None
    if (not verify_states(states)):
        return None
    
    #check expressions
    #check state machine declarations

    return config


def load_config(config_path):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config
    except BaseException as ex:
        print('could not open json config file')
        print(ex)
        return None
        



if __name__ == '__main__':
    config = load_config('config.json')
    if (config is not None):
        config = verify_config(config)
        if (config is not None):
            print('verified')
        else:
            print('config could not be verified')
        
        