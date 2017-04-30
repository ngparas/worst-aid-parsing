def is_911(sentence):
    return "Call 911" in sentence

def extract_911_clauses(sentence):
    clauses = sentence.split("if")
    return [{'type': '911-conditional', 'text': 'if'+clauses[i]} if i == 1 else {'type': '911-action', 'text': clauses[i]} for i in range(0, len(clauses))]

if __name__ == '__main__':
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
            print "Not a Call 911 sentence."
        print('\n')
