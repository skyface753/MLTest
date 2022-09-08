
from time import sleep
from game import Game
import random
import numpy as np
from keras import Sequential
from keras.models import load_model, model_from_json
from collections import deque
from keras.layers import Dens
import matplotlib.pyplot as plt
from keras.optimizers import Adam
# pip3 install tensorflow-macos
env = Game()

np.random.seed(0)
from keras.utils.vis_utils import plot_model


class DQN:

    """ Implementation of deep q learning algorithm """

    def __init__(self, action_space, state_space):

        self.action_space = action_space
        self.state_space = state_space
        self.epsilon = 1
        self.gamma = .95
        self.batch_size = 64
        self.epsilon_min = .01
        self.epsilon_decay = .995
        self.learning_rate = 0.001
        self.memory = deque(maxlen=100000)
        self.model = self.build_model()

    def build_model(self):
        try:
            # load json and create model
            json_file = open('model.json', 'r')
            print("Loaded model from disk")
            sleep(1)
            loaded_model_json = json_file.read()
            json_file.close()
            loaded_model = model_from_json(loaded_model_json)
            # load weights into new model
            loaded_model.load_weights("model.h5")
            loaded_model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
            return loaded_model
            # # return loaded_model
        except:
            print('No model found - creating new one')
            sleep(1)
            model = Sequential()
            model.add(Dense(64, input_shape=(self.state_space,), activation='relu'))
            model.add(Dense(64, activation='relu'))
            model.add(Dense(self.action_space, activation='linear'))
            model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
            model.trainable = True
            return model


    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):

        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_space)
        act_values = self.model.predict(state)
        # print(act_values)
        return np.argmax(act_values[0])

    def replay(self):

        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        states = np.array([i[0] for i in minibatch])
        actions = np.array([i[1] for i in minibatch])
        rewards = np.array([i[2] for i in minibatch])
        next_states = np.array([i[3] for i in minibatch])
        dones = np.array([i[4] for i in minibatch])

        states = np.squeeze(states)
        next_states = np.squeeze(next_states)

        targets = rewards + self.gamma*(np.amax(self.model.predict_on_batch(next_states), axis=1))*(1-dones)
        targets_full = self.model.predict_on_batch(states)

        ind = np.array([i for i in range(self.batch_size)])
        targets_full[[ind], [actions]] = targets

        self.model.fit(states, targets_full, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

def train_dqn(episode):

    loss = []

    action_space = 3
    state_space = 5
    # max_steps = 1000
    
    RENDER_EVERY = 1
    hitsList = []
    agent = DQN(action_space, state_space)
    for e in range(episode):
        state = env.reset()
        state = np.reshape(state, (1, state_space))
        score = 0
        # for i in range(max_steps):
        
        while True:
            action = agent.act(state)
            reward, next_state, done = env.step(action, e % RENDER_EVERY == 0)
            score += reward
            next_state = np.reshape(next_state, (1, state_space))
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            agent.replay()
            if done:
                hitsList.append(env.hitsPerGame)
                print("episode: {}/{}, score: {}".format(e, episode, score))
                break
        loss.append(score)
        plt.plot([e for e in range(len(loss))], loss)
        plt.title('Loss')
        plt.ion()
        plt.draw()
        plt.pause(0.001)
        plt.plot([e for e in range(len(hitsList))], hitsList)
        plt.title('Hits till death')
        plt.ion()
        plt.draw()
        plt.pause(0.001)
        if(len(loss) % 5 == 0):
            # serialize model to JSON
            model_json = agent.model.to_json()
            with open("model.json", "w") as json_file:
                json_file.write(model_json)
            # serialize weights to HDF5
            agent.model.save_weights("model.h5")
            print("Saved model to disk")
            
            plot_model(agent.model, to_file='./dqn_model.png', show_shapes=True)
            
    print("Episode: {}/{}, score: {}".format(e, episode, score))
    return loss


if __name__ == '__main__':

    ep = 100
    loss = train_dqn(ep)
    plt.plot([i for i in range(ep)], loss)
    plt.xlabel('episodes')
    plt.ylabel('reward')
    plt.show()
