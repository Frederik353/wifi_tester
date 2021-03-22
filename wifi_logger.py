# importerer nodvnedige libraryer

import sys
import os
import platform
import ipaddress
import asyncio
from datetime import datetime as dt
import speedtest

# erklerer globale variabler
my_list_of_tasks = []
my_tasks = []
nbr_host_found = 0
list_of_hosts_found = []

# asynkron funksjon for aa send ping til spesifiser ip paa lokalt nettverk
async def ping_coroutine(cmd, ip):

   global nbr_host_found, list_of_hosts_found

   running_coroutine = await asyncio.create_subprocess_shell(
      cmd,
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE)

   # vent for svar paa ping 
   stdout = await running_coroutine.communicate()

   # hvis svar inneholder time to live inkluder ip i liste
   # og inkrementer antall enheter funnet
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
      # deklarere verdier brukt i objekt
      self.nbr_host_found = 0
      self.list_of_hosts_found = []

      # fil hvor lokale ip adresser funnet blir lagret
      self.filename = "hosts.txt"

      # tester om ip adresse er riktig
      try:
            self.network = ipaddress.ip_network(ip_and_prefix)
      except:
            sys.exit("Incorrect network/prefix " + ip_and_prefix)

      self.nbr_host = self.network.num_addresses

      if self.network.num_addresses > 2:
            self.nbr_host -= 2

      # kommando som skrives inn i terminal
      self.one_ping_param = "ping -n 1 -l 1 -w 1000 " if platform.system().lower() == "windows" else "ping -c 1 -s 1 -w 1 "

   # funksjon for aa skrive inn data i csv fil
   def write_file(self, filename="speedtest.csv"):
      ret = 0
      now = dt.now()
      time = now.strftime("%d/%m/%Y,%T")
      try:
         with open(filename, "a") as f:
               if os.stat(filename).st_size == 0:
                  f.write("Date,Time,Ping (ms),Download (Mbit/s),Upload (Mbit/s),number of hosts online, url, latitude, longitude, location, country, countrycode, ISP, id, host, d, latency \n")
               f.write(f"{time},{self.download},{self.upload},{self.ping},{self.nbr_host_found},{self.server}\n")

      except Exception:
         ret = 1

      return ret

   def run(self):
      global my_tasks, nbr_host_found, list_of_hosts_found, my_list_of_tasks

      # kjorer speedtest
      st = speedtest.Speedtest()
      # lagrer resultater
      # merk download og upload i multithread mode
      self.download = st.download()
      self.upload = st.upload()
      self.ping = st.results.ping
      # self.server = str(st.get_best_server()).replace(",", "     ")
      self.server = list(st.get_best_server().values())



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

         # hvis kjores paa vindows kjor asyncio loop'er med IOCP
         if platform.system().lower() == "windows":
            asyncio.set_event_loop_policy(
            asyncio.WindowsProactorEventLoopPolicy())

         asyncio.run(ping_loop())

         self.list_of_hosts_found = list_of_hosts_found
         self.nbr_host_found = nbr_host_found



if __name__ == '__main__':

   # lokal ip adresse og cidr notasjon for subnet maske
   my_network = "192.168.10.0/24"


   my_scan = Networkscan(my_network)


   # skriv inn data i csv fil og  print ut masse data for debugging
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

