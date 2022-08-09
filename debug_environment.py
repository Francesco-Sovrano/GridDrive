import time
from grid_drive import GridDrive

env = GridDrive(culture_level="Hard", partial_observability=False)

def run_one_episode (env):
	env.seed(38)
	env.reset()
	sum_reward = 0
	done = False
	print('GridDrive started')
	while not done:
		# print('Pick a direction: NORTH = 0, SOUTH = 1, EAST  = 2, WEST  = 3')
		# direction = int(input())
		# print('Pick a speed in [0,120] that is a multiple of 10')
		# speed = int(input())
		# action = direction*env.MAX_GAPPED_SPEED + speed//env.SPEED_GAP
		action = env.action_space.sample()
		state, reward, done, info = env.step(action)
		sum_reward += reward
		env.render()
		time.sleep(0.25)
	print('GridDrive finished')
	return sum_reward

sum_reward = run_one_episode(env)