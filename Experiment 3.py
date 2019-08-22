
# coding: utf-8

# In[24]:


import numpy as np
from matplotlib import style
import matplotlib.pyplot as plt
import seaborn as sns


# ------------------define object: client------------------------#
class Client(object):
    def __init__(self, arrive_time):
        self.server = None   # Server that is object to client
        self.arrive_time = arrive_time  # Client's arrival time
        self.wait_time = 0 # Client's waiting time
        self.serve_time = 0 # Client's starting time to receive service
        self.leave_time = 0 # Client's leaving time

    def Set_Server(self, server):
        self.server = server # set server for client
        self.serve_time = self.server.serve_time 
        self.leave_time = self.arrive_time + self.wait_time + self.serve_time #leave time=arrival time+ wait time+ service time


# ---------------------define object:server-------------------#
class Server(object):
    def __init__(self, serve_time):
        self.serve_time = serve_time # each server has it's service rate
        self.used = False # whether this server is used
        self.starting_time = [] # the starting service time for this server
        self.ending_time = [] # the ending service time for this server


class Queue(object):
    def __init__(self, Client_list, Server_list):
        self.available = [] # available server by now
        self.current_time = 0 # time now
        self.Client_list = Client_list
        self.Server_list = Server_list

    def process(self):
        for server in self.Server_list:
            self.available.append(server)

        #print("The number of rest clients: " + str(len(self.Client_list)))
        while len(self.Client_list) != 0:

            client = self.Client_list[0] # get the first client in list
            self.current_time = client.arrive_time + client.wait_time# time now= arrival time + waiting time

            for server in self.Server_list:
                #if server is being used, and time now is over the ending service time, which means this server is available again, then add this server to available list
                if (server.used == True) and (self.current_time >= (server.starting_time[-1] + server.serve_time-0.00001)):
                    
                    server.used = False
                    self.available.append(server)

            if len(self.available) != 0:  # the waiting time of current client is 0
                #if there are servers idle, client will choose the idle server with bigggest service rate, eg best choice.
                best_server = self.available[0]
                if len(self.available) > 1:
                    for server in self.available:
                        if server.serve_time < best_server.serve_time:
                            best_server = server

                client.Set_Server(best_server) # allocate the best server to client
                best_server.used = True # best server is busy
                self.available.remove(best_server) # delete this best server from available list
                best_server.starting_time.append(client.arrive_time + client.wait_time)  # As the waiting time is 0, the starting serve time is "arrive_time"
                best_server.ending_time.append(client.leave_time)
                self.Client_list.pop(0) #  end this client,leave this system


            else: #  if all the servers are busy
                waiting1 = self.Server_list[0].starting_time[-1] + self.Server_list[0].serve_time - self.current_time  # time to wait for Server1
                waiting2 = self.Server_list[1].starting_time[-1] + self.Server_list[1].serve_time - self.current_time  # time to wait for Server2
                waiting3 = self.Server_list[2].starting_time[-1] + self.Server_list[2].serve_time - self.current_time  # time to wait for Server3
                client.wait_time = min(waiting1, waiting2, waiting3) # the waiting time should be the minimal
            #print("The number of rest clients: " + str(len(self.Client_list)))
        #print("\n")

def main(mu1,k,opt=None,om=None):
    
    lamda = 1 # clients' arrival follows Possion Distribution
    TOTAL_TIME = total_time
    # set service rate to three servers. The service time follows Exponential Distribution
    serve_time1 = np.random.exponential(1/mu1)
    #print(serve_time1)
    serve_time2 = np.random.exponential(1/k)
    serve_time3 = np.random.exponential(1/k)

    # -----randomly generate the client's arrival time in total simulation time---------#
    first_client = np.random.poisson(lam=lamda, size=1)
    t = first_client
    arrive_time = []
    while t < TOTAL_TIME:
        interval = np.random.poisson(lam=lamda, size=1) + 0.1
        arrive_time = np.append(arrive_time, t)
        t = t + interval

    # ---------------generate clients----------------------------#
    Client_list = []
    for i in range(len(arrive_time)):
        Client_list.append(Client(arrive_time[i]))

    
    # ---------------------generate servers---------------------#
    Server1 = Server(serve_time1)
    Server2 = Server(serve_time2)
    Server3 = Server(serve_time3)
    Server_list = [Server1, Server2, Server3]

    queue = Queue(Client_list, Server_list)

    queue.process()
    starting1 = queue.Server_list[0].starting_time
    ending1 = queue.Server_list[0].ending_time
    starting2 = queue.Server_list[1].starting_time
    ending2 = queue.Server_list[1].ending_time
    starting3 = queue.Server_list[2].starting_time
    ending3 = queue.Server_list[2].ending_time


    # collect the client data in total simulation time. eg reject the client if his leaving time is out of total simulation time.
    starting1_observed = []
    ending1_observed = []

    for i in range(len(starting1)):
        if ending1[i] <= TOTAL_TIME:
            starting1_observed.append(starting1[i])
            ending1_observed.append(ending1[i])

    starting2_observed = []
    ending2_observed = []
    for i in range(len(starting2)):
        if ending2[i] <= TOTAL_TIME:
            starting2_observed.append(starting2[i])
            ending2_observed.append(ending2[i])
 
    starting3_observed = []
    ending3_observed = []
    for i in range(len(starting3)):
        if ending3[i] <= TOTAL_TIME:
            starting3_observed.append(starting3[i])
            ending3_observed.append(ending3[i])

    # calculate the idle time
    diff1 = list(map(lambda x: x[0] - x[1], zip(ending1_observed, starting1_observed))) 
    idle1 = TOTAL_TIME - sum(diff1)
    if opt == True:
        print("The idle time of Server1 is: " + str(idle1))

    diff2 = list(map(lambda x: x[0] - x[1], zip(ending2_observed, starting2_observed))) 
    idle2 = TOTAL_TIME - sum(diff2)
    #print("The idle time of Server2 is: " + str(idle2))

    diff3 = list(map(lambda x: x[0] - x[1], zip(ending3_observed, starting3_observed))) 
    idle3 = TOTAL_TIME - sum(diff3)
    #print("The idle time of Server3 is: " + str(idle3))

    return idle1

def f(idletime,total_time,mu,p,q):
    
    Utility = -(-np.log(idletime/total_time)*p-q*(mu**2)) # ulitily function -(ln(idle rate)*p-q*mu^2)
    return Utility

if __name__ == '__main__':
    
    
    #golden section method . the single variable is server 1 's service rate, eg mu_1'
    K_list=[]
    mu_star=[]
    utility_list=[]
    k=0.5
    p=1
    q=10
    rate=q/p
    Rate_list=[]
    while rate < 50: #by changing other two servers' service rate to get different optimal mu for server 1
        total_time = 200 # total simulation time 
        a = 0.1
        b = 10
        tol = 0.00001
        gr = 0.618
        x_1 = b-(b-a)*gr
        x_2 = a+(b-a)*gr
        opt = False
        while abs(x_2-x_1) > tol:
            if f(main(x_1,k),total_time,x_1,p,q) < f(main(x_2,k),total_time,x_2,p,q):
                b = x_2
            else:
                a = x_1
            x_1 = b-(b-a)*gr
            x_2 = a+(b-a)*gr
        optimal_mu = (a+b)/2
        opt = True
        om = True
        max_utility = -f(main(optimal_mu,k,opt),total_time,optimal_mu,p,q)
        mu_star.append(optimal_mu)
        Rate_list.append(rate)
        rate=rate+1   
        print("The q/p rate is",rate)
        print("The optimal mu is:",optimal_mu)
        print("The max utility of server 1 is ",max_utility)


fig = plt.figure(figsize = (8,6))
optimal_mu, = plt.plot(Rate_list,mu_star,label = 'mu_star',color='k')
#max_utility,= plt.plot(Rate,utility_list,label="utility_list")

        
plt.title(("Queuing problem random simulation experiment").title())
#plt.ylim(ymin =0, ymax = 2)
plt.xlabel("q/p rate")
plt.ylabel("Optimal mu for server1")
plt.show()

