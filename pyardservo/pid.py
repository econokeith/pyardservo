import time

class PIDController:
    
    def __init__(self, kP=1, kI=0, kD=0):
        self.kP = kP
        self.kI = kI
        self.kD = kD
        
    def initialize(self):
        self.time_curr = time.time()
        self.time_prev = self.time_curr
        
        self.error_prev = 0
        self.cP = 0
        self.cI = 0
        self.cD = 0
        
    def update(self, error, sleep=0.01):
        
        time.sleep(sleep)
        self.time_curr = time.time()
        time_delta = self.time_curr - self.time_prev
        error_delta = error - self.error_prev
        
        self.cP = error
        self.cI += error * time_delta
        self.cD = (error_delta / time_delta) if time_delta > 0 else 0
        
        self.time_prev = self.time_curr
        self.error_prev = error
        
        self.correction = sum([self.kP * self.cP, self.kI * self.cI, self.kD * self.cD])
        
        return self.correction