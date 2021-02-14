import sys
import os
import platform
import ipaddress
import asyncio
from datetime import datetime as dt 
import speedtest


my_list_of_tasks = []
my_tasks = []
nbr_host_found = 0
list_of_hosts_found = []


async def ping_coroutine(cmd, ip):

   global nbr_host_found, list_of_hosts_found

   running_coroutine = await asyncio.create_subprocess_shell(
      cmd,
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE)

   stdout = await running_coroutine.communicate()

   if "ttl=" in str(stdout).lower():

      nbr_host_found += 1
      list_of_hosts_found.append(ip)

async def ping_loop():

   global my_tasks, my_list_of_tasks

   for each_task_list in my_list_of_tasks:
      for each_coroutine in asyncio.as_completed(each_task_list):
         await each_coroutine


class Networkscan:

   def __init__(self, ip_and_prefix):

      self.nbr_host_found = 0
      self.list_of_hosts_found = []

      self.filename = "hosts.txt"

      try:
            self.network = ipaddress.ip_network(ip_and_prefix)
      except:
            sys.exit("Incorrect network/prefix " + ip_and_prefix)

      self.nbr_host = self.network.num_addresses

      if self.network.num_addresses > 2:
            self.nbr_host -= 2

      self.one_ping_param = "ping -n 1 -l 1 -w 1000 " if platform.system().lower() == "windows" else "ping -c 1 -s 1 -w 1 "

   def write_file(self, filename="speedtest.csv"):
      ret = 0

      # data = ""
      # for i in self.list_of_hosts_found:
      #    data += i + "\n"
         # with open(filename, "w") as f:
         #    f.write(data)

      now = dt.now()
      time = now.strftime("%d/%m/%Y,%T")
      try:
         with open(filename, "a") as f:
               if os.stat(filename).st_size == 0:
                  f.write("Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s),number of hosts online\n")
               f.write(f"{time},{self.download},{self.upload},{self.ping},{self.nbr_host_found}\n")

      except Exception:
         ret = 1

      return ret

   def run(self):
      global my_tasks, nbr_host_found, list_of_hosts_found, my_list_of_tasks

      # speedtest
      st = speedtest.Speedtest()

      self.download = st.download()
      self.upload = st.upload()
      self.ping = st.results.ping

      # check for hosts
      self.nbr_host_found = 0
      self.list_of_hosts_found = []
      my_tasks = []
      nbr_host_found = 0
      list_of_hosts_found = []

      i = 128

      my_list_of_tasks = []

      my_list_of_tasks.append(my_tasks)

      if self.network.num_addresses != 1:
         for host in self.network.hosts():

            cmd = self.one_ping_param + str(host)
            my_tasks.append(ping_coroutine(cmd, str(host)))
            i -= 1
            if i <= 0:
                  i = 128
                  my_tasks = []
                  my_list_of_tasks.append(my_tasks)
            else:
               host = str(self.network.network_address)
               cmd = self.one_ping_param + host
               my_tasks.append(ping_coroutine(cmd, host))

         # print(str(len(my_list_of_tasks)))

         if platform.system().lower() == "windows":
            asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy())

         asyncio.run(ping_loop())

         self.list_of_hosts_found = list_of_hosts_found
         self.nbr_host_found = nbr_host_found






if __name__ == '__main__':

   my_network = "192.168.10.0/24"

   my_scan = Networkscan(my_network)

   print("Network to scan: " + str(my_scan.network))
   print("Prefix to scan: " + str(my_scan.network.prefixlen))
   print("Number of hosts to scan: " + str(my_scan.nbr_host))
   print("Scanning hosts...")

   my_scan.run()


   print("List of hosts found:")

   for i in my_scan.list_of_hosts_found:
      print(i)


   print("Number of hosts found: " + str(my_scan.nbr_host_found))

   res = my_scan.write_file()

   if res:
      print("Write error with file " + my_scan.filename)

   else:
      print("Data saved into file " + my_scan.filename)

   # print object properties
   my_scan.tail = 1
   temp = vars(my_scan)
   for item in temp:
      print(item, ':', temp[item])

