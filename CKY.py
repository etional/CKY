import sys
import getopt
import os

class CKY:
  def __init__(self):
    """CKY algorithm initialization"""
    self.non_terminals = []
    self.sigma = []

  # read rule text file and create a dictionary of rules
  def readRules(self, fileName):
    f = open(os.path.join(os.getcwd(), fileName))
    rules = {}
    for line in f:
      rule = {}
      r, p = line.split("\t")
      r = r.strip()
      non_term, derives = r.split("  ")
      if non_term not in self.non_terminals:
        self.non_terminals.append(non_term)
        rules[non_term] = []
      if " " in derives:
        first, second = derives.split(" ")
        prob = float(p.replace("\n", ""))
        rules[non_term].append([first, second, prob])
      else:
        prob = float(p.replace("\n", ""))
        rules[non_term].append([derives, prob])
        if derives not in self.sigma:
          self.sigma.append(derives)
    f.close()
    return rules

  # read sentences text file and create a list of sentences
  def readSentences(self, fileName):
    sentences = []
    f = open(os.path.join(os.getcwd(), fileName))
    for line in f:
      sentences.append(line.replace("\n", ""))
    f.close()
    return sentences

  # syntactic parsing using CKY algorithm
  def parsing(self, rules, sentence):
    words = sentence.split()
    # Initialize pi table and backpoint table
    pis = []
    bps = []
    for i in range(len(words)):
      row_p = []
      row_b = []
      for j in range(len(words)):
        pi = {}
        bp = {}
        row_p.append(pi)
        row_b.append(bp)
      pis.append(row_p)
      bps.append(row_b)
    
    # Initialize CKY algorithm
    for i in range(len(words)):
      for x in self.non_terminals:
        for rule in rules[x]:
          if len(rule) == 2:
            if rule[0] == words[i]:
              pis[i][i][x] = rule[1]
              break
          pis[i][i][x] = 0.0

    # CKY algorithm
    for l in range(1, len(words)):
      for i in range(len(words) - l):
        j = i + l
        span = words[i]
        for k in range(i + 1, j + 1):
          span = span + " " + words[k]
        for x in self.non_terminals:
          prob, s, arg1, arg2 = self.max_pi(i, j, rules[x], pis)
          if prob > 0.0:
            pis[i][j][x] = prob
            bps[i][j][x] = [s, arg1, arg2]    
    return pis, bps

  # calculate maximum pi value
  def max_pi(self, i, j, rules, pis):
    split = i
    maximum = 0.0
    arg1 = ""
    arg2 = ""
    for s in range(i, j):
      for rule in rules:
        if len(rule) == 3:
          for y in pis[i][s].keys():
            for z in pis[s + 1][j].keys():
              if rule[0] == y and rule[1] == z:
                a = rule[2]
                b = pis[i][s][y]
                c = pis[s + 1][j][z]
                pi = rule[2] * pis[i][s][y] * pis[s + 1][j][z]
                if pi > maximum:
                  maximum = pi
                  split = s + 1
                  arg1 = y
                  arg2 = z
    return maximum, split, arg1, arg2

  # write a result of the syntactic parsing in a text file
  def writeParsing(self, pis, bps, sentence):
    f = open("output.txt", "a")
    f.write('PROCESSING SENTENCE %s\n' % sentence)
    words = sentence.split()
    for i in range(len(words)):
      f.write('SPAN:  %s\n' % words[i])
      for x in pis[i][i].keys():
        if pis[i][i][x] > 0:
          f.write('P(%s) = %g\n' % (x, pis[i][i][x]))
      f.write("\n")
    
    for l in range(1, len(words)):
      for i in range(len(words) - l):
        j = i + l
        span = words[i]
        for k in range(i + 1, j + 1):
          span = span + " " + words[k]
        f.write('SPAN:  %s\n' % span)
        for x in pis[i][j].keys():
          if pis[i][j][x] > 0:
            prob = pis[i][j][x]
            s = bps[i][j][x][0]
            arg1 = bps[i][j][x][1]
            arg2 = bps[i][j][x][2]
            f.write('P(%s) = %g (BackPointer = (%d,%s,%s))\n' % (x, prob, s, arg1, arg2))
        f.write("\n")
    f.close()
    
# create object for CKY algorithm, read rules and sentences,
# and perform syntactic parsing
def parseDir(grammarDir, sentencesDir):
  parser = CKY()
  rules = parser.readRules(grammarDir)
  sentences = parser.readSentences(sentencesDir)
  f = open("output.txt", "w")
  f.write("")
  f.close()
  for sentence in sentences:
    pis, bps = parser.parsing(rules, sentence)
    parser.writeParsing(pis, bps, sentence)


def main():
  (options, args) = getopt.getopt(sys.argv[1:], '')
  
  if len(args) == 2:
    parseDir(args[0], args[1])

if __name__ == "__main__":
    main()
