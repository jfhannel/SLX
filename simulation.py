import SLX
import numpy as np
import matplotlib.pyplot as plt

def plotState(state):
	ind = np.arange(self.min)

	N = 5
	menMeans = (20, 35, 30, 35, 27)
	menStd = (2, 3, 4, 1, 2)

	ind = np.arange(state.minRate(), self.maxRate())  # the x locations for the groups
	width = 1       # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(ind, state.demandAtRates(), width, color='r', yerr=menStd)

	womenMeans = (25, 32, 34, 20, 25)
	womenStd = (3, 5, 2, 3, 3)
	rects2 = ax.bar(ind + width, womenMeans, width, color='y', yerr=womenStd)

	# add some text for labels, title and axes ticks
	ax.set_ylabel('Scores')
	ax.set_title('Scores by group and gender')
	ax.set_xticks(ind + width)
	ax.set_xticklabels(('G1', 'G2', 'G3', 'G4', 'G5'))

	ax.legend((rects1[0], rects2[0]), ('Men', 'Women'))


	def autolabel(rects):
	    # attach some text labels
	    for rect in rects:
	        height = rect.get_height()
	        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
	                '%d' % int(height),
	                ha='center', va='bottom')

	autolabel(rects1)
	autolabel(rects2)

	plt.show()


state = SLX.State(
	{
		'A': 15,
		'D': [],
		'B': [[1]],
		'R': [],
		'r': 0.5
	},
	1,
	0.5
)

sctyScenario = [
	[[2,3], []],
	[[3,5], []],
	[[6,7,5,5], []],
	[[8,7,6,4], []],
	[[6,5,8,5,7,9,10], []],
	[[], []],
	[[], []]
]

for i in xrange(len(sctyScenario)):
	state.evolve(sctyScenario[i][0], sctyScenario[i][1])
	plotState(state)

