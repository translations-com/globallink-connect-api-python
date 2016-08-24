class PDCustomAttribute:
	mandatory = 'false'
	name = ''
	type = ''
	values = []
	def __init__(self, customAttribute = None):
		if customAttribute != None:
			self.mandatory = customAttribute.mandatory
			self.name = customAttribute.name
			self.type = customAttribute.type
			self.values = customAttribute.values
			