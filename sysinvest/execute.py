from sysinvest.common.monitor import Monitor
from sysinvest.common.collector import Collector
from queue import Queue
import sysinvest.common.api as API


def execute( configuration, as_thread = False ):
    API.QUEUE = Queue()
    processMonitor = Monitor( configuration )
    collector = Collector( configuration )
    collector.start()
    if as_thread:
        processMonitor.start()

    else:
        processMonitor.run()

    return