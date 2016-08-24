class PDWorkflow:
	name = ''
	ticket = ''
	def __init__(self, externalWorkflow):
		self.name = externalWorkflow.name
		self.ticket = externalWorkflow.ticket
