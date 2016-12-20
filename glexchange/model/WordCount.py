class PDWordCount:
	golden = None
	exact_100 = None
	fuzzy = None
	repetitions = None
	nomatch = None
	total = None
	def __init__(self, golden, exact_100, repetitions, nomatch, total):
		self.golden = golden
		self.exact_100 = exact_100
		self.repetitions = repetitions
		self.nomatch = nomatch
		self.total = total
		self.fuzzy = total - golden - exact_100 - repetitions - nomatch
		