"""
Input generator for lab cooling cabinet (Python 2.7)
Gregor Ulm, 2016
Chalmers University of Technology

Features:
- door openings modelled using Markov process with three states
- variable door opening times
- all six doors operated independently


High-level description:

1)
Create a list of transitions, starting out in state "closed" for each door.

2)
Process list of transitions, and adding randomness for the following:
. door movement in sec.
. time a door remains in a state in sec. before moving on to the next state

Door open up to roughly 90 degrees. Degrees are converted to some larger
number. A value of 6000 presents a (nearly) full opening, and the state
"open", while a value of 3000 represents the state "half-open".

Door movements are "dampened", i.e. 90 % of a door opening movement are done
with a speed of x (a random value within a predefined range), the next 5 %
with a speed of x/2, and the last 5 % with a speed of x/4.


Output format:
column 1: time stamp in ms
column 2: current angle of door 1
...
column 7: current angle of door 6

e.g.
...
21599920;4055,89579864;6000;217,203748633;1946,02105549;0;2376,68748002;;;;;;
21599930;4027,72037543;6000;177,864998624;1975,50622299;0;2321,78880547;;;;;;
21599940;3999,54495222;6000;138,526248615;2004,9913905;0;2266,89013093;;;;;;
21599950;3971,36952901;6000;118,85687361;2034,47655801;0;2211,99145638;;;;;;
...

Idiosyncracies are that a comma is used as a decimal separator, and that empty
columns are specified. The former is due to German software settings being used,
where commas take the place of decimal points. Empty columns are necessary as
it is the expected input of the program that consumes the produced CSV file.
"""

import time
import random
from random import randint

start_time = time.time()

print "Processing."

FILENAME = "Lab_6doors_1h.csv"

# number of iterations; 5000 is enough for 6 hours
NUM = 5000

STEPS = 360000  # 1 hour
#STEPS = 2160000 # 6 hours

# 1 min   =       60000 ms
# 1 hour  =  60 * 60000 ms  -> steps:  6 * 60000
# 6 hours = 360 * 60000 ms  ->        36 * 60000



# State transitions:
#
# State: closed
A1 = 0.4    # closed -> closed
A2 = 0.3    # closed -> half-open
A3 = 0.3    # closed -> open
#
# State: half-open
B1 = 0.8    # half-open -> closed
B2 = 0.1    # half-open -> half-open
B3 = 0.1    # half-open -> open
#
# State: open
C1 = 0.7    # open -> closed
C2 = 0.1    # open -> half-open
C3 = 0.2    # open -> open

assert A1 + A2 + A3 == 1.0
assert B1 + B2 + B3 == 1.0
assert C1 + C2 + C3 == 1.0

# deliminiting time spent in states
CLOSED_MIN    = 1
CLOSED_MAX    = 30
HALF_OPEN_MIN = 2
HALF_OPEN_MAX = 8 
OPEN_MIN      = 5
OPEN_MAX      = 15

def nextState(state):
  """
  Move to the next state in the Markov process, based on the current state.
  """
  assert isinstance(state, tuple)
  
  (st_closed, st_halfopen, st_open) = state
  
  val = random.random()
  res = None
  
  if st_closed:
    assert A1 + A2 + A3 == 1.0
    
    # closed -> closed
    if val <= A1:
      res = state
      
    # closed -> half-open
    elif val <= A1 + A2:
      res = (False, True, False)
    
    # closed -> open
    else:
      res = (False, False, True)
  
  elif st_halfopen:
    assert B1 + B2 + B3 == 1.0
    
    # half-open -> closed
    if val <= B1:
      res = (False, False, True)
    
    # half-open -> half-open
    elif val <= B1 + B2:
      res = state
      
    # half-open -> open
    else:
      res = (True, False, False)
  
  elif st_open:
    assert C1 + C2 + C3 == 1.0
    
    # open -> closed
    if val <= C1:
      res = (True, False, False)
    
    # open -> half-open
    elif val <= C1 + C2:
      res = (False, True, False)
    
    # open -> open
    else:
      res = state

  assert sum(res) == 1
  
  return res



def getState(state):
  assert isinstance(state, tuple)
  """ Converts state into textual representation. """
  
  (a, b, c) = state
  
  assert sum(state) == 1
  
  if a:
    return "closed"
  elif b:
    return "half-open"
  elif c:
    return "open"



def getIncrementHalf():
  # between 0.75 and 1.25 sec (excl. dampening)
  duration_ms = random.uniform(0.75, 1.25) * 1000
  # from 0 to step size 3000
  return int( (3000.0 / duration_ms) * 10 )

  

def getIncrementFull():
  # "closed" to "open", between 1.5 and 2.5 sec
  duration_ms = random.uniform(1.5, 2.5) * 1000
    
  # from 0 to step size 6000
  return int( (6000.0 / duration_ms) * 10 )
  
  

def processState(st, nextSt):
  
  assert st     in ["open", "half-open", "closed"]
  assert nextSt in ["open", "half-open", "closed"]
  
  tmp = []
  
  # for each starting state, stay in that state for a number of
  # seconds; afterwards, transition to next state
  
  if st == "closed":
    
    # closed for 1 to 30 seconds
    val = randint(CLOSED_MIN, CLOSED_MAX)
  
    # number of 10 ms steps:
    steps = (val * 1000) / 10
  
    for i in range(steps):
      tmp.append(0)
      
    if nextSt == "closed":
      pass

    if nextSt == "half-open":
          
      # from 0 to step size 3000
      inc = getIncrementHalf()
      
      tmp = []
      x   = 0
      while True:
        
        if x < 2700:
          tmp.append(x)
          x += inc
          
        elif x < 2850:
          tmp.append(x)
          x += (inc / 2)
          
        elif x < 3000:
          tmp.append(x)
          x += (inc / 4)
          
        else:
          tmp.append(3000)
          break
          
    if nextSt == "open":
      # from 0 to step size 6000
      inc = getIncrementFull()
      
      tmp = []
      x   = 0
      while True:
        
        if x < 5400:
          tmp.append(x)
          x += inc
          
        elif x < 5700:
          tmp.append(x)
          x += (inc / 2)
          
        elif x < 6000:
          tmp.append(x)
          x += (inc / 4)
          
        else:
          tmp.append(6000)
          break
          
          
  elif st == "half-open":
    
    # half-open for 3 to 10 seconds
    val = randint(HALF_OPEN_MIN, HALF_OPEN_MAX)
  
    # number of 10 ms steps:
    steps = (val * 1000) / 10
  
    for i in range(steps):
      tmp.append(3000) # angle when half-open
    
    
    if nextSt == "half-open":
      pass
        
        
    if nextSt == "closed":
      # from 3000 to step size 0
      inc = getIncrementHalf()
      
      tmp = []
      x   = 3000
      while True:
        
        if x > 300:
          tmp.append(x)
          x -= inc
          
        elif x > 150:
          tmp.append(x)
          x -= (inc / 2)
          
        elif x > 0:
          tmp.append(x)
          x -= (inc / 4)
          
        else:
          tmp.append(0)
          break

    if nextSt == "open":
      # from 3000 to step size 6000
      inc = getIncrementHalf()
      
      tmp = []
      x   = 3000
      while True:
        
        if x < 5400:
          tmp.append(x)
          x += inc
          
        elif x < 5700:
          tmp.append(x)
          x += (inc / 2)
          
        elif x < 6000:
          tmp.append(x)
          x += (inc / 4)
          
        else:
          tmp.append(6000)
          break
          

  elif st == "open":
    
    # open for 5 to 15 seconds
    val = randint(OPEN_MIN, OPEN_MAX)
  
    # number of 10 ms steps:
    steps = (val * 1000) / 10
  
    for i in range(steps):
      tmp.append(6000) # angle when open
      
    if nextSt == "open":
      pass
      
    if nextSt == "half-open":
      # from 6000 to 3000
      inc = getIncrementHalf()
      
      tmp = []
      x   = 6000
      while True:
        
        if x > 3300:
          tmp.append(x)
          x -= inc
          
        elif x > 3150:
          tmp.append(x)
          x -= (inc / 2)
          
        elif x > 3000:
          tmp.append(x)
          x -= (inc / 4)
          
        else:
          tmp.append(3000)
          break

    if nextSt == "closed":
      # from 6000 to angle 0
      inc = getIncrementFull()
      
      tmp = []
      x   = 6000
      while True:
        
        if x > 300:
          tmp.append(x)
          x -= inc
          
        elif x > 150:
          tmp.append(x)
          x -= (inc / 2)
          
        elif x > 0:
          tmp.append(x)
          x -= (inc / 4)
          
        else:
          tmp.append(0)
          break

  return tmp


doors = ["d1", "d2", "d3", "d4", "d5", "d6"]

states = dict()

# create list of transitions for all doors
for door in doors:
  val = []
  currentState = (True, False, False)

  i = 0
  while True:
    val.append( getState(currentState) )
    currentState = nextState(currentState)
    i += 1
    if i > NUM:
      break
  states[door] = val


instructions = dict()

for door in doors:
  val = []
  tmp = states[door]

  for i in range(len(tmp) - 1):
    val += processState( tmp[i], tmp[i + 1] )

  instructions[door] = val


# create CSV with timestamps
f = open(FILENAME, "w")

vals_d1 = instructions["d1"]
vals_d2 = instructions["d2"]
vals_d3 = instructions["d3"]
vals_d4 = instructions["d4"]
vals_d5 = instructions["d5"]
vals_d6 = instructions["d6"]


for lst in [vals_d1, vals_d2, vals_d3, vals_d4, vals_d5, vals_d6]:

  # safety check: all values in admissible range for robot arms
  for x in lst:
    assert x >= 0 and x <= 6000
    
  for i in range(1, len(lst)):
    assert abs(lst[i-1] - lst[i]) <= 100
    
    
for i in range(STEPS):
  timestamp = i * 10
  
  tmp =   str(timestamp)       + ";"    \
        + str(int(vals_d1[i])) + ";"    \
        + str(int(vals_d2[i])) + ";"    \
        + str(int(vals_d3[i])) + ";"    \
        + str(int(vals_d4[i])) + ";"    \
        + str(int(vals_d5[i])) + ";"    \
        + str(int(vals_d6[i])) + ";\n"


  tmp = tmp.replace(".", ",")  # input uses "," instead of decimal point
  f.write(tmp)



# close doors, i.e. move robot arms back to position 0 at the end
length = (6000 / 50) + 1

close_d1 = [int(vals_d1[i+1])] + [0] * length
close_d2 = [int(vals_d2[i+1])] + [0] * length
close_d3 = [int(vals_d3[i+1])] + [0] * length
close_d4 = [int(vals_d4[i+1])] + [0] * length
close_d5 = [int(vals_d5[i+1])] + [0] * length
close_d6 = [int(vals_d6[i+1])] + [0] * length

for lst in [close_d1, close_d2, close_d3, close_d4, close_d5, close_d6]:
  
  for i in range(1, len(lst)):
    tmp = lst[i - 1] - 50
    if tmp < 0:
      tmp = 0
    lst[i] = tmp
    
    
for lst in [close_d1, close_d2, close_d3, close_d4, close_d5, close_d6]:
  
  for x in lst:
    assert x >= 0 and x <= 6000
  
  for i in range(1, len(lst)):
    assert abs(lst[i-1] - lst[i]) <= 100
    

    

for i in range(len(close_d1)):
  timestamp += 10
  
  tmp =   str(timestamp)        + ";"      \
        + str(int(close_d1[i])) + ";"      \
        + str(int(close_d2[i])) + ";"      \
        + str(int(close_d3[i])) + ";"      \
        + str(int(close_d4[i])) + ";"      \
        + str(int(close_d5[i])) + ";"      \
        + str(int(close_d6[i])) 

  tmp = tmp.replace(".", ",")  # input uses "," instead of decimal point
  f.write(tmp)

f.close()

print "File written.\n Total execution time: "
print round(time.time() - start_time, 1), "seconds"
