#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Tools to monitor CPU and GPU usage, as well as runtimes.
# 
# Author: Marcus Kasdorf
# Date:   July 29, 2021

import psutil
from threading import Thread
import time
import matplotlib.pyplot as plt
from numpy import asarray, ndindex, mean, logical_and, sum, seterr

_GPU = False

class BufferTime:
    """
    Context manager to add buffer time when entering
    and exiting the context.

    Parameters
    ----------
    buffer_time : float
        Buffer time when entering and exiting 
        the context.

    """
    def __init__(self, buffer_time):
        self._buffer_time = buffer_time

    def __enter__(self):
        time.sleep(self._buffer_time)
        return self

    def __exit__(self, type, value, traceback):
        time.sleep(self._buffer_time)

    @property
    def buffer_time(self):
        return self._buffer_time

try:
    import GPUtil
    
    class MonitorGPU(Thread):
        """
        Creates a separate thread to monitor GPU usage. Can be 
        using as a context manager or as a standalone object.

        Parameters
        ----------
        delay : float
            Seconds between usage calls.

        """
        def __init__(self, delay):
            super(MonitorGPU, self).__init__()

            self.stopped = False                    # Stopped status
            self.delay = delay                      # Time between calls to GPUtil
            self.log = []                           # Usage log
            self.time_log = []                      # Time log
            self.start_time = time.perf_counter()   # Log the start time

        def run(self):
            while not self.stopped:
                self.log.append(GPUtil.getGPUs()[0].load * 100)
                self.time_log.append(time.perf_counter() - self.start_time)
                time.sleep(self.delay)

        def stop(self):
            self.stopped = True

        def __enter__(self):
            self.start()
            return self

        def __exit__(self, type, value, traceback):
            self.stop()

        def plot(self):
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))
            ax.stackplot(self.time_log, self.log)
            ax.set_xlabel("Time elapsed (seconds)")
            ax.set_ylabel("GPU percent usage")
            ax.grid(alpha=0.5)
            plt.show()

    _GPU = True
            
except ImportError:
    print("GPUtil package not found, MonitorGPU class will be not be created.")

class MonitorCPU(Thread):
    """
    Creates a separate thread to monitor CPU usage. Can be 
    using as a context manager or as a standalone object.

    Parameters
    ----------
    delay : float
        Seconds between usage calls.

    buffer : float
        Buffer time before and after the activity
        to be averaged.

    """
    def __init__(self, delay, buffer=0):
        super(MonitorCPU, self).__init__()

        self.stopped = False                    # Stopped status
        self.delay = delay                      # Time between calls to psutil
        self.log = []                           # Usage log
        self.time_log = []                      # Time log
        self.start_time = time.perf_counter()   # Log the start time
        self._cpu_count = psutil.cpu_count()    # Get number of logical cores
        self._buffer_time = buffer              # Set buffer time to correct averages
        
    def run(self):
        while not self.stopped:
            self.log.append(psutil.cpu_percent(self.delay, percpu=True))
            self.time_log.append(time.perf_counter() - self.start_time)
            time.sleep(self.delay)

    def stop(self):
        self.stopped = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def plot(self):
        if 2 * self._buffer_time > self.time_log[-1]:
            raise ValueError(f"Buffer time of {2 * self._buffer_time} too long for elapsed time of {self.time_log[-1]}")

        fig = plt.figure(figsize=(16, 6))
        shape = (3, 8)

        data = asarray(self.log)
        time_array = asarray(self.time_log)    

        ax = plt.subplot2grid(shape, (0, 0), rowspan=3, colspan=4)
        lines = ax.stackplot(time_array, data.T, labels=[str(i) for i in range(len(self.log[0]))])
        ax.set_xlabel("Time elapsed (seconds)")
        ax.set_ylabel("CPU percent usage")
        ax.set_title(
            f"Total CPU Usage (Avg: {mean(sum(data[logical_and(self._buffer_time < time_array, time_array < (time_array[-1] - self._buffer_time))], axis=1)):.2f})"
        )
        ax.legend(loc="upper right", title="CPU #")
        ax.grid(alpha=0.5)

        for i, ind in enumerate(ndindex(3, 4)):
            if i > self._cpu_count:
                break

            data = asarray(self.log)[:, i]
            
            ax = plt.subplot2grid(shape, (ind[0], 4+ind[1]))
            ax.plot(time_array, data, color=lines[i].get_facecolor()[0])
            ax.set_title(
                f"CPU {i} (Avg: {mean(data[logical_and(self._buffer_time < time_array, time_array < (time_array[-1] - self._buffer_time))]):.2f})"
            )
            ax.set_ylim(0, 100)
            ax.grid(alpha=0.5)

        fig.tight_layout()
        plt.show()

class Runtime:
    """
    Context manager to measure the runtime of the
    code in the contained block.

    Parameters
    ----------
    message : str
        Output message to print before printing
        the elapsed time.

    Attributes
    ----------
    elapsed_time : float
        Contained the elapsed runtime of the context.
        This value will be None until the context is closed.

    """
    def __init__(self, message="Time elapsed"):
        self._message = message
        self._start_time = None
        self._end_time = None
        self._elapsed = None
    
    def __enter__(self):
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self._end_time = time.perf_counter()
        self._elapsed = self._end_time - self._start_time
        if self._message:
            if type is None:
                print(f"{self._message}: {self._elapsed}")
            else:
                print(f"(ended abruptly) {self._message}: {self._elapsed}")

    @property
    def elapsed(self):
        return self._elapsed

# Testing code
if __name__ == "__main__":
    seterr(all="raise")

    x, y = range(100000), range(100000)
    with Runtime() as t:
        for i in range(len(x)):
            x[i] + y[i]

    print(t.elapsed)