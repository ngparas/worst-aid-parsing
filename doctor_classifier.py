"""Classifier for doctor-related conditionals
"""

DOCTOR_KEYPHRASES = ["call a doctor",
                     "call your child's doctor",
                     "when to see a doctor",
                     "when to call a doctor",
                     "see a doctor",
                     "call the doctor"]

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
    if "if" in sentence:
        clauses = sentence.split("if")
        return [{'type': 'doctor-conditional', 'text': 'if' + clauses[i]} if i == 1
                else {'type': 'doctor-action', 'text': clauses[i]} for i in range(0, len(clauses))]
    else:
        return [{'type': 'doctor-conditional', 'text': sentence}]

if __name__ == "__main__":
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
