"""Classify Statements as either Actions, Conditionals, or Informational
"""
import re

import spacy

# use some garbage globals until we know what this app will look like
nlp = spacy.load('en')

def split_sentences(text):
    """Util function to parse sentences

    This function uses Spacy to parse sentences

    Args:
        text (string): a text string to be split into sentences
   
    Return:
        A list of strings
    """

    parsed_text = nlp(text)
    return [i.text for i in parsed_text.sents]


def is_action(sentence):
    """Predicate to determine if a sentence is an action

    This function returns true if a sentence from an online medical
    procedure is an action (e.g. a step) or not. It could also be
    an informational sentence or a conditional.

    Args:
        sentence (String): A sentence from a medical procedure

    Return:
        Boolean: True if an action, else False
    """

    tagged_sentence = nlp(sentence)

    # catch some special cases up front
    if tagged_sentence[0].text.lower() == 'continue':
        return True

    result = True
    verb_counter = 0
    for token in tagged_sentence:
        # Find a verb, we can tell impaeratives from verbs with an implied 'you'
        if token.pos_ == 'VERB':
            verb_counter += 1
            if token.text.lower() != 'is':
                if not any(i.dep_ in ['nsubj', 'nsubjpass'] for i in token.children):
                    result = result and True
                else:
                    result = result and False
            else:
                result = result and False

    if verb_counter > 0:
        return result
    else:
        return True

def extract_conditional_clauses(sentence):
    """Function to extract if clauses from a sentence

    This function takes a sentence and returns the conditional and
    unconditional clauses.

    Args:
        sentence (String): A sentence from a medical procedure

    Return:
        A Dict with two key value pairs. 'conditionals' has a list
            of the conditional clauses. 'nonconditionals' has a
            list of the rest of the clauses.
    """
    tagged_sentence = nlp(sentence)
    tagged_sentence_text = tagged_sentence.text

    excluded_clauses = ['if necessary',
                        'if possible']

    conditional_heads = [i.head for i in tagged_sentence if i.text.lower() in ['if']]
    conditional_phrases = [" ".join(j.text for j in i.subtree) for i in conditional_heads]

    # much efficient, very code
    cond_results = []
    for i in conditional_phrases:
        if sum(1 for j in conditional_phrases if i in j) == 1:
            if i.lower() not in excluded_clauses:

                cond_results.append(i.replace(" ,", ",").replace(" .", "."))
                # Found conditional clauses, now get the rest of it

    min_match_index = None
    max_match_index = None
    for clause in cond_results:
        match = re.search(clause, tagged_sentence_text)
        if match is not None:
            if min_match_index is None or match.start() < min_match_index:
                min_match_index = match.start()
            if max_match_index is None or match.end() > max_match_index:
                max_match_index = match.end()

    # subset string to stuff outside of matches
    # TODO : be more clever about this
    if min_match_index is None or max_match_index is None:
        rest = tagged_sentence_text
    else:
        rest = tagged_sentence_text[:min_match_index] + tagged_sentence_text[max_match_index:]
        rest = rest.replace(" ,", ",").replace(" .", ".")

    return {"conditionals": cond_results,
            "nonconditionals": rest}

if __name__ == '__main__':
    samples = ["Rest the sprained or strained area.",
               "If necessary, use a sling for an arm injury or crutches for a leg or foot injury.",
               "Splint an injured finger or toe by taping it to an adjacent finger or toe.",
               "Ice for 20 minutes every hour.",
               "Never put ice directly against the skin or it may damage the skin.",
               "Use a thin towel for protection.",
               "Compress by wrapping an elastic (Ace) bandage or sleeve lightly (not tightly) around the joint or limb.",
               "Specialized braces, such as for the ankle, can work better than an elastic bandage for removing the swelling.",
               "Elevate the area above heart level if possible.",
               "Give an over-the-counter NSAID (non-steroidal anti-inflammatory drug) like ibuprofen (Advil, Motrin), acetaminophen (Tylenol), or aspirin.",
               "Do not give aspirin to anyone under age 19.",
               "There is a 'popping' sound with the injury.",
               "Continue RICE for 24 to 48 hours, or until the person sees a doctor.",
               "The doctor may want to do X-rays or an MRI to diagnose a severe sprain or strain or rule out a broken bone.",
               "The doctor may need to immobilize the limb or joint with a splint, cast, or other device until healing is complete.",
               "Physical therapy can often be helpful to bring an injured joint back to normal.",
               "In severe cases, surgery may be needed.",
               "If the nail is torn, use sterile scissors to cut off rough edges to prevent further injury.",
               "use sterile scissors to cut off rough edges to prevent further injury.",
               "Use sterile scissors to cut off rough edges if the nail is torn",
               "Make an appointment with a doctor if you still have pain after two weeks of home treatment, if the knee becomes warm, or if you have fever along with a painful, swollen knee."]


    # for s in samples:
    #     print("\n")
    #     print(s)
    #     print(is_action(s))

    extract_conditional_clauses("Make an appointment with a doctor if you still have pain after two weeks of home treatment, if the knee becomes warm, or if you have fever along with a painful, swollen knee.")

    for s in samples:
        print(s)
        print(extract_conditional_clauses(s))
        print('\n')
