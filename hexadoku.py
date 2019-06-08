import time, random
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits   = '0123456789ABCDEF'
rows     = 'abcdefghijklmnop'
cols     = digits
squares  = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('abcd','efgh','ijkl','mnop') for cs in ('0123','4567','89AB','CDEF')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)

################ Unit Tests ################

def test():
    "A set of tests that must pass."
    assert len(squares) == 256
    assert len(unitlist) == 48
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 39 for s in squares)
    assert units['c2'] == [['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2', 'i2', 'j2', 'k2', 'l2', 'm2', 'n2', 'o2', 'p2'], 
                           ['c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'cA', 'cB', 'cC', 'cD', 'cE', 'cF'], 
                           ['a0', 'a1', 'a2', 'a3', 'b0', 'b1', 'b2', 'b3', 'c0', 'c1', 'c2', 'c3', 'd0', 'd1', 'd2', 'd3']]
    assert (peers['c2'] == set(['a2', 'b2', 'd2', 'e2', 'f2', 'g2', 'h2', 'i2', 'j2', 'k2', 'l2', 'm2', 'n2', 'o2', 'p2',
                              'c0', 'c1', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'cA', 'cB', 'cC', 'cD', 'cE', 'cF',
                             'a0', 'a1', 'a3', 'b0', 'b1', 'b3', 'd0', 'd1', 'd3']))
    print('All tests pass.')

################# Parse a Grid ################

def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s,d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.)
    return values

def grid_values(grid):
    "Convert grid into a dict of {square: char} with  or '.' for empties."
    chars = [c for c in grid if c in digits or c in '.']
    assert len(chars) == 256
    return dict(zip(squares, chars))

################ Constraint Propagation ################

def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False
    
def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values ## Already eliminated
    values[s] = values[s].replace(d,'')
    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        return False ## Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values

################ Display as 2-D grid ################

def display(values):
    "Display these values as a 2-D grid."
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*4)]*4)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '37B' else '')
                      for c in cols))
        if r in 'dhl': break
    print()

def count(values):
    "Display these values as a 2-D grid."
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*4)]*4)
    ss = ""
    for r in rows:
        s = ''.join(values[r+c].center(width)+('')
                      for c in cols)
        ss += s
        if r in 'dhl': break
    bb = ss.split()
    for i in range(len(bb)):
        bb[i] = int(rev_d[bb[i]])
    return bb[0]

################ Search ################

def solve(grid): return search(parse_grid(grid))

def search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!
    ## Chose the unfilled square s with the fewest possibilities
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d))
                for d in values[s])

################ Utilities ################

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
        if e: return e
    return False

def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return file(filename).read().strip().split(sep)

def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq

################ System test ################
d ={
    '1':'0',
    '2':'1',
    '3':'2',
    '4':'3',
    '5':'4',
    '6':'5',
    '7':'6',
    '8':'7',
    '9':'8',
    '10':'9',
    '11':'A',
    '12':'B',
    '13':'C',
    '14':'D',
    '15':'E',
    '16':'F',
    '?':'.'
    }

rev_d ={
    '0':'1',
    '1':'2',
    '2':'3',
    '3':'4',
    '4':'5',
    '5':'6',
    '6':'7',
    '7':'8',
    '8':'9',
    '9':'10',
    'A':'11',
    'B':'12',
    'C':'13',
    'D':'14',
    'E':'15',
    'F':'16',
    '?':'.',
    '|':''
    }

def solve_all(grids, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""
    assert len(grids) == 1
    def time_solve(grid):
        start = time.clock()
        values = solve(grid)
        t = time.clock()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values:
                display(values)
        return values
    values = [time_solve(grid) for grid in grids]
    total = count(values[0])
    return total

def solved(values):
    def unitsolved(unit): return set(values[s] for s in unit) == set(digits)
    return values is not False and all(unitsolved(unit) for unit in unitlist)

def random_puzzle(N=31):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 15:
            return ''.join(values[s] if len(values[s])==1 else '.' for s in squares)
    return random_puzzle(N) ## Give up and make a new puzzle


cc = 0
if __name__ == '__main__':
    with open('hard.txt','r') as r:
        n = int(r.readline())
        for i in range(n):
            conString = ""
            for j in range(16):
                s = r.readline()
                b = s.split()
                print(len(b))
                for k in range(len(b)):
                    b[k] = d[b[k]]
                s = "".join(b)
                conString += s
            print(conString)
            cc += solve_all([conString],"eee",0.0)
            r.readline()
        print(cc)
            
            
    #solve_all([random_puzzle() for _ in range(10)], "random", 0.0)



