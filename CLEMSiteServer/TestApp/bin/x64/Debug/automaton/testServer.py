
from fromMSite.microadapterAtlas import MicroAdapterAtlas
import logging
import time

logger = logging.getLogger('example_logger')

msc_server = MicroAdapterAtlas()  # Microscope handling MicroAdapterSEMTest()
msc_server.setLogger(logger)


error, message, sec_key = msc_server.connect()
msc_server.sec_key = sec_key
#msc_server.sec_key = 'VZ6Co1PajGuXWoVUORPG1A'
# msc_server.pause()
#time.sleep(120)
error, d = msc_server.setAutoCP("C:\\")
if (error):
    print(error)