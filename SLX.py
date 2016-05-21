import random

class State:
	################################################
	# self.state represents the SL market for a 
	# 	single security. It has 5 elements:
	# A: number of shares available to be borrowed
	# D: list of outstanding demanded shares; format:
	# 		[[time demanded, reservation rate],...]
	# B: list of currently borrowed shares; format:
	# 		[[reservation rate],...]
	# R: list of shares on recall; format:
	# 		[[time recalled, reservation rate],...]
	# r: current market rate
	################################################

	# recall age is the minimum time a share must be in recall
	# 	before being bought in - to allow borrower a chance to
	# 	increase reservation rate
	# init_rate is mostly a convenience, it has no impact on
	# 	long term rate evolution
	def __init__(self, init_state, init_recall_age, init_rate):
		self.state = init_state
		self.recall_age = init_recall_age
		self.rate = init_rate
		self.time = 0

	def age(self):
		self.time += 1

	def addBorrowDemands(self, demandReservationRates):
		self.state['D'].extend([[self.time, r] for r in demandReservationRates])

	def addReturns(self, returns):
		for r in returns:
			self.state['B'].remove(r)
		self.state['A'] += sum([1 for ret in returns])

	def numSharesDemanded(self):
		return sum([1 for d in self.state['D']])

	def numAvailShares(self):
		return self.state['A']

	def maxDemandReservationRate(self):
		if (len(self.state['D']) == 0):
			return -float('inf')
		return max([d[1] for d in self.state['D']])

	def minDemandReservationRate(self):
		if (len(self.state['D']) == 0):
			return float('inf')
		return min([d[1] for d in self.state['D']])

	def mktRate(self):
		return self.rate

	# returns demanded share with highest reservation rate
	# ties are broken via time priority, then uniformly chosen
	def topDemand(self):
		if (self.numSharesDemanded() == 0):
			return
		maxDemandReservationRate = self.maxDemandReservationRate()
		topDemands = [d for d in self.state['D'] if (d[1] == maxDemandReservationRate)]
		earliestTopDemands = [d for d in topDemands if (d[0] == min([d[0] for d in topDemands]))]
		return random.choice(earliestTopDemands)

	# returns recalled share that is able to be bought in
	# 	which has lowest reservation rate
	def bottomMatureRecall(self):
		if (self.numMatureRecalledShares() == 0):
			return
		minMatureRecalledReservationRate = self.minMatureRecalledReservationRate()
		bottomRecalls = [r for r in self.state['R'] if ((self.time - r[0]) >= self.recall_age and r[1] == minMatureRecalledReservationRate)]
		earliestBottomRecalls = [r for r in bottomRecalls if (r[0] == min([r[0] for r in bottomRecalls]))]
		return random.choice(earliestBottomRecalls)

	# lend share from available shares to the top demanded share order,
	# 	set market rate to min reservation rate of borrowed shares
	def lendShareFromAvail(self):
		self.state['A'] -= 1

		maxDemandReservationRate = self.maxDemandReservationRate()
		topDemand = self.topDemand()
		self.state['D'].remove(topDemand)
		self.state['B'].append([topDemand[1]])

		self.rate = self.minBorrowerReservationRate()

	# number of shares ready to be bought in
	def numMatureRecalledShares(self):
		return sum([1 for r in self.state['R'] if (self.time - r[0] >= self.recall_age)])

	def numRecalledShares(self):
		return sum([1 for r in self.state['R']])

	# minimum reservation rate of all shares currently borrowed
	def minBorrowerReservationRate(self):
		if (self.numSharesBorrowed() + self.numRecalledShares() == 0):
			return float('inf')
		if (self.numRecalledShares() == 0):
			return min([b[0] for b in self.state['B']])
		if (self.numSharesBorrowed() == 0):
			return min([r[1] for r in self.state['R']])
		return min(min([b[0] for b in self.state['B']]), min([r[1] for r in self.state['R']]))

	def maxBorrowerReservationRate(self):
		if (self.numSharesBorrowed() + self.numRecalledShares() == 0):
			return -float('inf')
		if (self.numRecalledShares() == 0):
			return max([b[0] for b in self.state['B']])
		if (self.numSharesBorrowed() == 0):
			return max([r[1] for r in self.state['R']])
		return max(max([b[0] for b in self.state['B']]), max([r[1] for r in self.state['R']]))

	# minimum reservation rate of any category
	def minRate(self):
		return min(self.minBorrowerReservationRate(), self.minDemandReservationRate())

	def maxRate(self):
		return max(self.maxDemandReservationRate(), self.maxBorrowerReservationRate())

	# buy in a buy-in-able share with the lowest reservation rate
	# lend it to the demanded share order with highest reservation rate
	# set market rate to min borrowed share reservation rate
	def lendShareFromBuyIn(self):
		minMatureRecalledReservationRate = self.minMatureRecalledReservationRate()
		bottomMatureRecall = self.bottomMatureRecall()

		maxDemandReservationRate = self.maxDemandReservationRate()
		topDemand = self.topDemand()

		self.state['R'].remove(bottomMatureRecall)
		self.state['D'].remove(topDemand)
		self.state['D'].append([self.time, bottomMatureRecall[1]])
		self.state['B'].append([topDemand[1]])

		self.rate = self.minBorrowerReservationRate()

	def maxRecalledReservationRate(self):
		if (len(self.state['R']) == 0):
			return -float('inf')
		return max([r[1] for r in self.state['R']])

	def minMatureRecalledReservationRate(self):
		if (len(self.state['R']) == 0):
			return -float('inf')
		return min([r[1] for r in self.state['R'] if (self.time - r[0] >= self.recall_age)])

	def cancelRecall(self):
		maxRecalledReservationRate = self.maxRecalledReservationRate()
		topRecall = random.choice([r for r in self.state['R'] if (r[1] == maxRecalledReservationRate)])
		self.state['R'].remove(topRecall)

		self.state['B'].append([topRecall[1]])

	# move all shares with reservation rate less than max demanded reservation rate
	# 	from borrowed to recalled
	def recallShares(self):
		recallableShares = [b for b in self.state['B'] if (b[0] < self.maxDemandReservationRate())]
		for r in recallableShares:
			self.state['B'].remove(r)
			self.state['R'].append([self.time, r[0]])

	def numSharesBorrowed(self):
		return sum([1 for b in self.state['B']])

	def printState(self):
		print 'Time:', self.time
		print 'Market Rate:', self.rate
		print 'Min Borrower Reservation Rate:', self.minBorrowerReservationRate()
		print 'Avail Shares:', self.numAvailShares()
		print 'Borrowed Shares:', self.numSharesBorrowed()
		print 'Demanded Shares:', self.numSharesDemanded()
		print 'Max Demanded Reservation Rate:', self.maxDemandReservationRate()
		print 'Recalled Shares:', self.numRecalledShares()
		print 'Mature Recalled Shares:', self.numMatureRecalledShares()
		print '\n'

	def evolve(self, demandReservationRates, returns):
		# in each time period, demand orders come in, and returns happen
		# NOTE: these returns are specific borrowed share being returned by the borrower,
		# 	the case of a lender needing to get shares back within a fixed time period
		# 	has not yet been solved.
		self.addBorrowDemands(demandReservationRates)
		self.addReturns(returns)

		if (self.numSharesDemanded() > 0):

			# lend avail shares
			while (self.numSharesDemanded() > 0
				and self.numAvailShares() > 0):
				self.lendShareFromAvail()

			# lend buy-in shares
			while (self.numMatureRecalledShares() > 0
				and self.maxDemandReservationRate() > self.minBorrowerReservationRate()):
				self.lendShareFromBuyIn()


		# cancel invalid recalls
		while (self.maxRecalledReservationRate() > max(self.mktRate(), self.minBorrowerReservationRate())):
			self.cancelRecall()

		self.recallShares()
		self.age()

		self.printState()
