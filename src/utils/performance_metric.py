import time
import numpy

class PerformanceMetric:
    def __init__(self):
        self.clear()

    def step(self, batch_size):
        self.time_steps.append(time.time())
        self.batch_sizes.append(batch_size)

    def clear(self):
        self.time_steps  = []
        self.batch_sizes = []

    def get(self):
        time_steps  = numpy.array(self.time_steps) - self.time_steps[0]
        batch_sizes = numpy.array(self.batch_sizes)

        result = {}
        result["data_points_count"] = int(batch_sizes.sum())
        result["batch_count"]       = int(time_steps.shape[0])
        
        result["batch_time_mean"]   = round(float(time_steps.mean()), 5)
        result["batch_time_std"]    = round(float(time_steps.std()), 5)

        result["batch_time_s1"]     = numpy.percentile(time_steps, 68).item()
        result["batch_time_s2"]     = numpy.percentile(time_steps, 95).item()
        result["batch_time_s3"]     = numpy.percentile(time_steps, 99.7).item()


        return result