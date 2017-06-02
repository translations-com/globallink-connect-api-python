class PDWordCount:
	golden = None
	exact_100 = None
	fuzzy = None
	repetitions = None
	nomatch = None
	total = None
	def __init__(self, stats):
                if hasattr(stats, 'totalWordCount') :
                        self.total = stats.totalWordCount
                        self.fuzzy = self.total
                if hasattr(stats, 'goldWordCount') :
                        self.golden = stats.goldWordCount
                        if self.fuzzy != None :
                                self.fuzzy = self.fuzzy - self.golden
                if hasattr(stats, 'oneHundredMatchWordCount') :
                        self.exact_100 = stats.oneHundredMatchWordCount
                        if self.fuzzy != None :
                                self.fuzzy = self.fuzzy - self.exact_100
                if hasattr(stats, 'repetitionWordCount') :
                        self.repetitions = stats.repetitionWordCount
                        if self.fuzzy != None :
                                self.fuzzy = self.fuzzy - self.repetitions
                if hasattr(stats, 'noMatchWordCount') :
                        self.nomatch = stats.noMatchWordCount
                        if self.fuzzy != None :
                                self.fuzzy = self.fuzzy - self.nomatch
                
		
