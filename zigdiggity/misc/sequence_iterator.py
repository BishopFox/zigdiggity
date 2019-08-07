class SequenceIterator():

    def __init__(self, initial_value=0, value_limit=255):
        self.value = initial_value % value_limit
        self.value_limit = value_limit
    
    def __iter__(self):
        return self
    
    def next(self):
        result = self.value
        self.value = (self.value + 1) % self.value_limit
        return result