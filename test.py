




import speedtest
import os
# import re
# import subprocess
from datetime import datetime as dt 


# st = speedtest.Speedtest()

# download = st.download()
# upload = st.upload()
# ping = st.results.ping

download = 0
upload = 0
ping = 0

servernames =[]
# st.get_servers(servernames)


def log_to_file():
   ret = 0
   filename = "speedtest.csv"
   now = dt.now()
   time = now.strftime("%d/%m/%Y,%T")



   try:
      with open(filename, "a") as f:
         if os.stat(filename).st_size == 0:
            f.write("Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s)\n")
         f.write(f"{time},{download},{upload},{ping}\n")

   except Exception:
      ret = 1
   return ret



res = log_to_file()

if res:
   print("Write error with file ")

else:
   print("Data saved into file ")

