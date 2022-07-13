from collections import OrderedDict

with open('LucasCommits.txt') as f:
    lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    commitLines = [l for l in lines if 'commit' in l]   # only get lines w commit

commitLines.reverse() # commits are new->old : top->bottom
commits = OrderedDict()
for num, line in enumerate(commitLines):
    commits[num+1] = line.split(' ')[-1]

for num, com in commits.items():
    print('Commit {}:	{}'.format(num, com))
