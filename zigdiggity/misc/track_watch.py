import time

class TrackWatch():

    def __init__(self):
        self.differences = []
        self.last_click = None

    def click(self):
        if self.last_click is None:
            self.last_click = time.time()
        else:
            current_time = time.time()
            self.differences.append(current_time-self.last_click)
            self.last_click = current_time


    def variance(self):
        if len(self.differences)<2:
            return 100
        mean = self.mean()
        return sum([(diff - mean)**2 for diff in self.differences])/(len(self.differences)-1)

    def mean(self):
        if len(self.differences)==0:
            return 0
        return sum(self.differences) / len(self.differences)

