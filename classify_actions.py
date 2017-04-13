"""Classify Statements as either Actions, Conditionals, or Informational
"""

import spacy

# use some garbage globals until we know what this app will look like
nlp = spacy.load('en')

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
               "Use sterile scissors to cut off rough edges if the nail is torn"]


    for s in samples:
        print("\n")
        print(s)
        print(is_action(s))

