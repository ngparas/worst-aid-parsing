"""Classify Statements as either Actions, Conditionals, or Informational
"""
import re

import spacy

# use some garbage globals until we know what this app will look like
nlp = spacy.load('en')
CALL_911_KEYPHRASES = ["call 911"]
DOCTOR_KEYPHRASES = ["call a doctor",
                     "call your child's doctor",
                     "when to see a doctor",
                     "when to call a doctor",
                     "see a doctor",
                     "call the doctor"]
LOOP_WORDS = ["until", "while"]

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

    conditional_heads = [i.head for i in tagged_sentence if i.text.lower() in ['if', 'while', 'until']]
    conditional_phrases = [" ".join(j.text for j in i.subtree) for i in conditional_heads]

    # much efficient, very code
    cond_results = []
    for i in conditional_phrases:
        if sum(1 for j in conditional_phrases if i in j) == 1:
            if i.lower() not in excluded_clauses:

                cond_results.append(i)
                # Found conditional clauses, now get the rest of it

    min_match_index = None
    max_match_index = None
    rest = tagged_sentence_text
    for clause in cond_results:
        search_clause = ''.join(clause.split())
        search_clause = '\s*'.join(search_clause)
        match = re.search(search_clause, rest)
        if match is not None:
            if min_match_index is None or match.start() < min_match_index:
                min_match_index = match.start()
            if max_match_index is None or match.end() > max_match_index:
                max_match_index = match.end()

        # subset string to stuff outside of matches
        # TODO : be more clever about this
        if min_match_index is None or max_match_index is None:
            pass
        else:
            rest = rest[:min_match_index] + rest[max_match_index:]
            rest = rest.replace(" ,", ",").replace(" .", ".").replace(" '", "'")

        min_match_index = None
        max_match_index = None

    return {"conditionals": cond_results,
            "nonconditionals": rest}


def is_911(sentence):
    """Given a sentence, returns whether it relates to a 911 conditional

    Keyword arguments:
    sentence -- the string that contains the sentence
    """
    return any(keyphrase in sentence.lower() for keyphrase in CALL_911_KEYPHRASES)

def extract_911_clauses(sentence):
    """Given a sentence, returns a list of dictionary representations of the clauses

    Keyword arguments:
    sentence -- the string that contains the sentence
    """
    clauses = sentence.split("if")
    return {'substeps' : [], 'type': '911-conditional', 'text': sentence}



def is_doctor(sentence):
    """Given a sentence, returns whether it relates to a doctor conditional

    Keyword arguments:
    sentence -- the string that contains the sentence
    """
    return any(keyphrase in sentence.lower() for keyphrase in DOCTOR_KEYPHRASES)

def extract_doctor_clauses(sentence):
    """Given a sentence, returns a list of dictionary representations of the clauses

    Keyword arguments:
    sentence -- the string that contains the sentence
    """
    return {'substeps': [], 'type': 'doctor-conditional', 'text': sentence}



def is_loop_action(sentence):
	"""Returns true if sentence is an action containing a "loop word" as defined in LOOP_WORDS

	sentence -- string containing the sentence of interest
	"""
	# Looks like is_action needs some work, let's look into that
	# print(is_action(sentence))
	# print(any(loop_word in sentence.lower() for loop_word in LOOP_WORDS))
	# return is_action(sentence) and any(loop_word in sentence.lower() for loop_word in LOOP_WORDS)

	return any(loop_word in sentence.lower() for loop_word in LOOP_WORDS)

def extract_loop_action_clauses(sentence):
    """Returns a list of first aid graph nodes with the looping conditional type associated with the node.
        Use if is_loop_action(sentence) is true

        sentence -- string containing the sentence of interest
        """
    for loop_word in LOOP_WORDS:
        if loop_word in sentence.lower():
            clauses = extract_conditional_clauses(sentence)
            conditionals = clauses["conditionals"]
            loop_condition = next(x for x in conditionals if is_loop_action(x))
            action = sentence.replace(loop_condition, "")
            if not len(action) is 0:
                return {'type': loop_word + '-conditional', 'text': sentence, 'loop-condition': loop_condition, 'action': action}
            else:
                return {'type': loop_word + '-conditional', 'text': sentence, 'loop-condition': loop_condition, 'action': action}
    return {}





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

    print(extract_conditional_clauses("If the person doesn't respond, call 911 immediately and start CPR if necessary."))

    for s in samples:
        print(s)
        print(extract_conditional_clauses(s))
        print('\n')


    SAMPLES = [ "Avoid spicy or greasy foods and caffeinated or carbonated drinks until 48 hours after all symptoms have gone away.",
    			"Apply direct pressure until bleeding stops.",
    			"Flush with lukewarm water for 15 to 30 minutes.",
    			"For severe burns, continue flushing until you see a doctor or you arrive in an emergency room.",
    			"Don't rub eyes.",
    			"Apply ice and elevate hand to reduce swelling.",
    			"Avoid sex, tampons, or douching while you're bleeding.",
    			"Apply ice to reduce swelling while waiting for medical care.",
                "6. Monitor the Person Until Help Arrives"
    		  ]

    print(extract_conditional_clauses(SAMPLES[1]))
    for sample in SAMPLES:
    	if is_loop_action(sample):
    		print(extract_loop_action_clauses(sample))
    	else:
    		print("Not a loop action.")


    samples = ["Rest the sprained or strained area.",
               "If necessary, use a sling for an arm injury or crutches for a leg or foot injury.",
               "Call 911 NOW if:",
               "Call 911 NOW if the person is:",
               "Call 911 if the person has these symptoms of alcohol poisoning:",
               "Call 911 now if the person has had severe reactions in the past or has any of these symptoms:",
               "Call 911 if the person:",
               "Call 911",
               "Call 911 if:",
               "Call 911 if the person loses consciousness or has:"]

    for s in samples:
        print(s)
        if(is_911(s)):
            print(extract_911_clauses(s))
        else:
            print("Not a Call 911 sentence.")
        print('\n')

    SAMPLES = ["Call your child's doctor immediately if your child has any of the following:",
               "Call 911 NOW if:",
               "4. When to See a Doctor",
               "3. When to Call a Doctor",
               "Call a doctor if the person has:",
               "3. Ease Into Eating",
               "See a doctor immediately for these symptoms:",
               "Call the doctor as soon as possible if the person has:",
               "For a mild reaction:"]

    for s in SAMPLES:
        print(s)
        if is_doctor(s):
            print(extract_doctor_clauses(s))
        else:
            print("Not a doctor-related sentence.")
        print("\n")

"""Implement fuzzy match functionality with word vectors
"""
def word_vector_match(query, available_keys):
    max_similarity = 0
    max_key = None

    q = nlp(query)

    for key in available_keys:
        k = nlp(key)
        similarity = k.similarity(q)
        if similarity > max_similarity:
            max_similarity = similarity
            max_key = key

    return max_key, max_similarity 