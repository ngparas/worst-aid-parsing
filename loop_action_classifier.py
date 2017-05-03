from classify_actions import is_action

LOOP_WORDS = ["until", "while"]

def is_loop_action(sentence):
	"""Returns true if sentence is an action containing a "loop word" as defined in LOOP_WORDS

	sentence -- string containing the sentence of interest
	"""
	# Looks like is_action needs some work, let's look into that
	# print(is_action(sentence))
	# print(any(loop_word in sentence.lower() for loop_word in LOOP_WORDS))
	# return is_action(sentence) and any(loop_word in sentence.lower() for loop_word in LOOP_WORDS)

	return any(loop_word in sentence.lower() for loop_word in LOOP_WORDS)

def extract_loop_action_clause(sentence):
	"""Returns a list of first aid graph nodes with the looping conditional type associated with the node.
	Use if is_loop_action(sentence) is true

	sentence -- string containing the sentence of interest
	"""
	for loop_word in LOOP_WORDS:
		if loop_word in sentence:
			return {'type': loop_word + '-action', 'text': sentence}

if __name__ == "__main__":
	SAMPLES = [ "Avoid spicy or greasy foods and caffeinated or carbonated drinks until 48 hours after all symptoms have gone away.",
				"Apply direct pressure until bleeding stops.",
				"Flush with lukewarm water for 15 to 30 minutes.",
				"For severe burns, continue flushing until you see a doctor or you arrive in an emergency room.",
				"Don't rub eyes.",
				"Apply ice and elevate hand to reduce swelling.",
				"Avoid sex, tampons, or douching while you're bleeding.",
				"Apply ice to reduce swelling while waiting for medical care."
			  ]

	for sample in SAMPLES:
		if is_loop_action(sample):
			print(extract_loop_action_clause(sample))
		else:
			print("Not a loop action.")