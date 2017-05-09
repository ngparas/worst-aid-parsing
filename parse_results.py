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

def parse_step(step_text):
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
                parsed_procedure.append({'text': parsed_conditionals.get('conditionals'),
                                             'type': 'conditional'})
            if len(parsed_conditionals.get('nonconditionals')) > 0:
                nc = parsed_conditionals.get('nonconditionals')
                if is_action(nc):
                    parsed_procedure.append({'text': nc,
                                             'type': 'action'})
                else:
                    parsed_procedure.append({'text': nc,
                                             'type': 'info'})
    return parsed_procedure

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
            parsed_procedure += extract_911_clauses(step)
            for substep in procedure.get('steps').get(step):
                parsed_procedure.append({'text': substep.get('text'),
                                         'type': '911-conditional-list-item'})
        elif is_doctor(step):
            parsed_procedure += extract_doctor_clauses(step)
            for substep in procedure.get('steps').get(step):
                parsed_procedure.append({'text': substep.get('text'),
                                         'type': 'doctor-conditional-list-item'})
        else:
            parsed_procedure += parse_step(step)

            for substep in procedure.get('steps').get(step):
                parsed_procedure += parse_step(substep.get('text'))

    return parsed_procedure

def add_pointers(graph):
    """Walk the graph to add in navigation pointers

    Args:
        graph (Dict): Graph parsed from webmd scraped results

    Return:
        A graph (Dict) with navigation pointers
    """
    size = max(graph.keys())
    for i in range(1, size):
        node_type = graph[i].get('type')
        if node_type in ['911-conditional', 'doctor-conditional']:
            ptr = None #TODO : how to represent end of graph
            for j in range(i+1, size):
                if 'item' not in graph[j].get('type'):
                    ptr = j
                    break
            graph[i]['true'] = i + 1
            graph[i]['false'] = ptr
        elif node_type == 'conditional':
            graph[i]['true'] = i + 1
            graph[i]['false'] = i + 2

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

    graph = add_pointers(graph)
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(graph)

if __name__ == '__main__':

    main()
