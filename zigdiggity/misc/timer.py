import time

class Timer():

    def __init__(self, time_limit=1):
        self.start_time = time.time()
        self.time_limit = time_limit
    
    def set_time_limit(self, time_limit):
        self.time_limit = time_limit
    
    def reset(self):
        self.start_time = time.time()

    def has_expired(self):
        return time.time() - self.start_time > self.time_limit

    def time_passed(self):
        return time.time() - self.start_time
