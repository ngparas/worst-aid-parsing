"""Parse a single scraped json result into nodes
"""

import json
import pprint

from classify_actions import is_action
from classify_actions import extract_conditional_clauses
from classify_actions import split_sentences
from call_911_classifier import is_911
from call_911_classifier import extract_911_clauses
from doctor_classifier import is_doctor
from doctor_classifier import extract_doctor_clauses
from loop_action_classifier import is_loop_action, extract_loop_action_clauses


def load_results(results_path):
    """Load the results json

    This simple util function loads the results from the
    webmd web scraper

    Args:
        results_path (String): the path to the results json

    Return:
        A python Dict with the parsed results json
    """

    with open(results_path, 'r') as rf:
        return json.loads(rf.read().replace('\n', ''))

def parse_step(step_text, links, is_main_step):
    """Parse one step into its component nodes

    Args:
        step_text (String): the step text to parse into nodes

    Return:
        A list of dicts
    """
    parsed_procedure = []

    step_sentences = split_sentences(step_text)
    for step in step_sentences:

        # deals with loop action case
        if is_loop_action(step):
            parsed_procedure += extract_loop_action_clauses(step)

        else:
            parsed_conditionals = extract_conditional_clauses(step)
            if len(parsed_conditionals.get('conditionals')) > 0:
                parsed_procedure.append(generate_step_entry(parsed_conditionals.get('conditionals'), 'conditional', links, is_main_step))
            if len(parsed_conditionals.get('nonconditionals')) > 0:
                nc = parsed_conditionals.get('nonconditionals')
                if is_action(nc):
                    parsed_procedure.append(generate_step_entry(nc, 'action', links, is_main_step))
                else:
                    parsed_procedure.append(generate_step_entry(nc, 'info', links, is_main_step))
    return parsed_procedure

def generate_step_entry(text, type, links, is_main_step):
    if is_main_step:
        return {'text': text,
                'type': type,
                'substeps': []}
    else:
        return {'text': text,
                'type': type,
                'links': links}

def parse_procedure(procedure):
    """Parse a full procedure into a list of nodes

    Args:
        procedure_dict (Dict): A procedure scraped from webmd

    Return:
        A list of nodes, where each node is a Dict
    """

    parsed_procedure = []

    for step in procedure.get('order'):
        if is_911(step):
            current_main_step = extract_911_clauses(step)
            for substep in procedure.get('steps').get(step):
                substep['type'] = '911-conditional-list-item'
                current_main_step['substeps'].append(substep)
            parsed_procedure += [current_main_step]
        elif is_doctor(step):
            current_main_step = extract_doctor_clauses(step)
            for substep in procedure.get('steps').get(step):
                substep['type'] = 'doctor-conditional-list-item'
                current_main_step['substeps'].append(substep)
            parsed_procedure += [current_main_step]
        else:
            current_main_step = parse_step(step, [], True)

            for substep in procedure.get('steps').get(step):
                current_main_step[0]['substeps'].append(parse_step(substep.get('text'), substep.get('links'), False))
            parsed_procedure += current_main_step

    return parsed_procedure

def add_pointers(graph):
    """Walk the graph to add in navigation pointers

    Args:
        graph (Dict): Graph parsed from webmd scraped results

    Return:
        A graph (Dict) with navigation pointers
    """
    size = max(graph.keys())
    for i in graph.keys():
        node_type = graph[i].get('type')
        if node_type in ['911-conditional', 'doctor-conditional']:
            ptr = None #TODO : how to represent end of graph
            for j in range(i+1, size):
                if 'item' not in graph[j].get('type'):
                    ptr = j
                    break
            graph[i]['true'] = i + 1 if (i + 1 <= size) else None
            graph[i]['false'] = ptr
        elif node_type == 'conditional':
            ptr = None
            for k in range(i+2, size):
                if graph[i].get('level') == graph[k].get('level'):
                    ptr = k
                    break
            graph[i]['true'] = i + 1 if (i + 1 <= size) else None
            graph[i]['false'] = k
        elif node_type in ['action', 'info']:
            graph[i]['true'] = i + 1 if (i + 1 <= size) else None
            graph[i]['false'] = i + 1 if (i + 1 <= size) else None

    return graph

def main():
    results = load_results('list-of-pages-webmd-results.json')
    sample_key = list(results.keys())[0]
    print(sample_key)
    sample_key = "http://www.webmd.com/first-aid/fainting-treatment"
    procedure = results.get(sample_key)

    parsed_procedure = parse_procedure(procedure)
    graph = {}
    for i, p in enumerate(parsed_procedure):
        graph[i] = p

    #graph = add_pointers(graph)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(graph)

if __name__ == '__main__':

    main()
