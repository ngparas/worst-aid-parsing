"""Parse a single scraped json result into nodes
"""

import json

from classify_actions import is_action
from classify_actions import extract_conditional_clauses
from classify_actions import split_sentences


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

        parsed_conditionals = extract_conditional_clauses(step)
        if len(parsed_conditionals.get('conditionals')) > 0:
            parsed_procedure.append({'step': parsed_conditionals.get('conditionals'),
                                         'type': 'conditional'})
        if len(parsed_conditionals.get('nonconditionals')) > 0:
            nc = parsed_conditionals.get('nonconditionals')
            if is_action(nc):
                parsed_procedure.append({'step': nc,
                                         'type': 'action'})
            else:
                parsed_procedure.append({'step': nc,
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
        # handling "Call 911" case
        additional_text = "If "
        action_text = "Call 911"

        if "911" in step:
            for substep in procedure.get('steps').get(step):
                new_text = additional_text + substep.get('text')
                parsed_procedure += parse_step(new_text)

            parsed_procedure += parse_step("Call 911")

        else:
            parsed_procedure += parse_step(step)

            for substep in procedure.get('steps').get(step):
                parsed_procedure += parse_step(substep.get('text'))

    return parsed_procedure
        


def main():
    results = load_results('list-of-pages-webmd-results.json')
    sample_key = list(results.keys())[0]
    print(sample_key)
    procedure = results.get(sample_key)

    parsed_procedure = parse_procedure(procedure)
    for p in parsed_procedure:
        print(p)

if __name__ == '__main__':

    main()
