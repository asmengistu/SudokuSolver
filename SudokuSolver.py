'''
Started as a solution to a ProjectEuler.net problem
http://projecteuler.net

Constraint Programming Ideas mainly inspired 
by Courera's Discrete Optimization class with Pascal Van Hentenryck

Written by Abel Mengistu, 2013

A grid is internally represented as a list(array) of squares:
 Each square is represented as: [int_value, set]
 where set is a set of possible values for that square if value = 0
'''

def solve(grid, sOutFile = None, currentDepth = 0):
	'''
	Solves a Sudoku puzzle and returns the solution as a list
	
	Keyword Arguments:
	grid -- should be a list of 81 integers,
			internal representation (valid input): [value, set(possible values)]
	sOutFile -- if provided, the grid is written out to the given file
				during every iteration before and after propagation
				if the propagation altered the grid
	'''
	#if writing intermediate steps to file, clear that file on first iteration
	if sOutFile and currentDepth == 0:
		with open(sOutFile, 'w') as f:
			f.write('')
	#create representation of grid from list of values
	if type(grid) == list:
		sudoku = []
		for i in grid:	
			p = set(range(1,10)) if i == 0 else set()
			sudoku.append([i, p])
	prune(sudoku)
	#oldG used to check if the propagation changed the grid
	oldG  = reprGrid(sudoku)
	if sOutFile:
		writeGridToFile(sudoku, sOutFile, currentDepth)
	propagate(sudoku)
	#write to file after propagating if the grid changed
	if sOutFile and reprGrid(sudoku) != oldG:	
		writeGridToFile(sudoku, sOutFile, currentDepth)
	
	#if we are in an invalid state, return None
	for s in sudoku:
		if s[0] == 0 and len(s[1]) == 0:
			return None
	
	#calculate frequency of all possible values in the grid
	frequency = {}
	for s in sudoku:
		if s[0] == 0:
			for p in s[1]:
				if p in frequency:
					frequency[p] += 1
				else:
					frequency[p] = 1
	
	#sort squares by number of possible values in ascending order
	# - we do this to increase probability of guessing correct value
	sortedIndices = [x[0] for x in sorted(zip(range(len(sudoku)), sudoku), \
		key = lambda x: len(x[1][1]))]
	for i in sortedIndices:
		s = sudoku[i]
		if s[0] == 0:
			#for each possible value, use the frequency from above to sort
			# - again to further increase probability of guessing correct value
			for possibleValue in sorted(s[1], key = lambda x: frequency[x]):
				branch = [x[0] for x in sudoku]
				branch[i] = possibleValue
				soln = solve(branch, sOutFile, currentDepth + 1)
				if soln and isSolved(soln):
					return soln
	
	return [x[0] for x in sudoku]

def propagate(sudoku):
	'''
	Called by solver after pruning.

	'''
	changed = True
	constraints = [getBox, getRow, getCol]
	while changed:
		changed = False
		#look for squares with only 1 possible option
		for i in range(len(sudoku)):
			s = sudoku[i]
			if len(s[1]) == 1:
				s[0] = s[1].pop()
				changed = True
				updateConstraints(sudoku, i, s[0])
		prune(sudoku)

		#look for squares with unique option in a group (row, column or box)
		#for example:
		#  if a box contains 3 squares with values (1,3), (3,6) and (3,6)
		#  we can deduce that the box with possible values (1,3) should take
		#  on the value 1.
		for constraint in constraints:
			for i in range(9):
				group = constraint(i)
				data = {}
				for index in group:
					square = sudoku[index]
					if square[0] == 0:
						for option in square[1]:
							if option in data:
								data[option][0] += 1
							else:
								data[option] = [1, index]
				for key in data.keys():
					if data[key][0] == 1:
						sudoku[data[key][1]][0] = key
						sudoku[data[key][1]][1] = set()
						forced = True
						updateConstraints(sudoku, data[key][1], key)

def updateConstraints(sudoku, idx, value):
	'''
	Given a grid whose square idx, just got updated to `value`, 
	updates the constraints on the grid by going through each
	group the square, `idx`, belongs in and removing `value`
	as a possible option in the neighbors
	'''
	constraints = [(toBox, getBox), (toRow, getRow), (toCol, getCol)]
	for key, get in constraints:
		for i in get(key(idx)):
			square = sudoku[i]
			if square[0] == 0:
				if value in square[1]: square[1].remove(value)

def isSolved(sudoku):
	"Returns True if a sudoku is solved"
	for i in sudoku:
		if (type(i) == int and i == 0) or\
			(type(i) == list and i[0] == 0):
			return False
	return True

def prune(sudoku):
	"Prunes a sudoku - i.e makes sure the constraints of Sudoku are satisfied"
	rows = [set(range(1,10)) for i in range(9)]
	cols = [set(range(1,10)) for i in range(9)]
	boxes = [set(range(1,10)) for i in range(9)]
	for i in range(len(sudoku)):
		if sudoku[i][0] != 0:
			row = toRow(i)
			if sudoku[i][0] in rows[row]: rows[row].remove(sudoku[i][0])
			col = toCol(i)
			if sudoku[i][0] in cols[col]: cols[col].remove(sudoku[i][0])
			box = toBox(i)
			if sudoku[i][0] in boxes[box]: boxes[box].remove(sudoku[i][0])
	for i in range(len(sudoku)):
		if sudoku[i][0] == 0:
			sudoku[i][1] &= (rows[toRow(i)])	#intersection_update
			sudoku[i][1] &= (cols[toCol(i)])
			sudoku[i][1] &= (boxes[toBox(i)])

def getRow(i):
	"Returns a list of indices for row i (0-indexed)"
	return range(i*9, (i+1)*9)

def getCol(i):
	"Returns a list of indices for col i (0-indexed)"
	return range(i, 73+i, 9)

def getBox(k):
	"Returns a list of indices for box i (0-indexed)"
	start = k/3 * 27 + k%3 * 3
	return range(start, start + 3) +\
			range(start + 9, start + 12) +\
			 range(start + 18, start + 21)

def toRow(idx):
	"Converts a grid-index [0-80] to a row index"
	return idx/9

def toCol(idx):
	"Converts a grid-index [0-80] to a col index"
	return idx%9

def toBox(idx):
	"Converts a grid-index [0-80] to a box index"
	return (toRow(idx)/3) * 3 + toCol(idx)/3

with open('sample-puzzles.txt','r') as source:
	puzzles = source.read().split('\n')

def getSampleGrid(i):
	"Gets a sample grid from the 50 grids in sample-puzzles.txt"
	return [int(x) for x in ''.join(puzzles[i*10:(i+1)*10][1:])]

def showGrid(g, isValueOnly = True):
	'''
	Prints a grid to the screen
	If isValueOnly is True, prints out '-' instead of possible 
	options, for squares that do not have a value
	'''
	print reprGrid(g, isValueOnly)

def reprGrid(g, isValueOnly = True):
	'''
	Returns a string representation of a grid
	If isValueOnly is True, '-' is used instead of possible 
	options, for squares that do not have a value
	'''
	ret = ''
	width = 3
	if type(g[0]) != int:
		if isValueOnly:
			g = ['-' if x[0] == 0 else x[0] for x in g]
		else:
			newG = []
			for i in g:
				if i[0] == 0:
					pvals ='('+ ','.join([str(x) for x in sorted(i[1])]) +')'
					newG.append(pvals)
					width = max(width, len(pvals))
				else: newG.append(i[0])
			g = newG

	for i in range(len(g)):
		if i != 0 and i % 9 == 0:
			ret += '\n'
			if i % 27 == 0:
				ret += '\n\n'
		if i%9 != 0 and i % 3 == 0:
			ret += '  '
		ret += '{:^{width}}'.format(g[i], width = width)
	return ret

def writeGridToFile(sudoku, fname = 'sudoku.txt', currentDepth = 0):
	"Writes the given grid, to a file"
	r = reprGrid(sudoku, False)
	lvl = str(currentDepth) if currentDepth > 1 else ''
	r = '\n'.join([lvl+'-'*currentDepth + x for x in r.split('\n')])
	with open(fname,'a') as f:
		f.write(r)
		f.write('\n\n\n\n')
