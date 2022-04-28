import gym
import numpy as np 
# 1. Load Environment and Q-table structure
env = gym.make('FrozenLake8x8-v1')
Q = np.zeros([env.observation_space.n,env.action_space.n])
# env.observation.n, env.action_space.n gives number of states and action in env loaded
# 2. Parameters of Q-learning
eta = .628
gma = .9
epis = 1200000
rev_list = [] # rewards per episode calculate
tenPercentRev = [] 
showEvery = 300000
# 3. Q-learning Algorithm
for i in range(epis):
    # Reset environment
    s = env.reset()
    rAll = 0
    d = False
    j = 0
    # Print every 10% 
    if i % (epis/10) == 0:
        print("Episode: ", i)
        print("Current Rewars: " + str(sum(tenPercentRev)/(epis/10)))
        tenPercentRev = []
    # print("Episode: ", i)
    #The Q-Table learning algorithm
    while j < 99:
        # print("J: ", j)
        # if i % (epis/10) == 0:
        #     env.render()
        # env.render()
        j+=1
        # Choose action from Q table
        a = np.argmax(Q[s,:] + np.random.randn(1,env.action_space.n)*(1./(i+1)))
        #Get new state & reward from environment
        s1,r,d,_ = env.step(a)
        #Update Q-Table with new knowledge
        Q[s,a] = Q[s,a] + eta*(r + gma*np.max(Q[s1,:]) - Q[s,a])
        rAll += r

        s = s1
        if d == True:
            break
    rev_list.append(rAll)
    tenPercentRev.append(rAll)
    # env.render()
print("Reward Sum on all episodes " + str(sum(rev_list)/epis))
print("Final Values Q-Table")
print(Q)