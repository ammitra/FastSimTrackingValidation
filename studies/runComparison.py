from collections import OrderedDict
import subprocess

def setULHistoBool(reverse=False):
    with open('FastSimulation/TrackingRecHitProducer/python/TrackingRecHitProducer_cfi.py', 'r') as file :
        filedata = file.read()
    if not reverse:
        filedata = filedata.replace('ULresolutionHistograms = False', 'ULresolutionHistograms = True')
    else:
	filedata = filedata.replace('ULresolutionHistograms = True', 'ULresolutionHistograms = False')
    with open('FastSimulation/TrackingRecHitProducer/python/TrackingRecHitProducer_cfi.py', 'w') as file:
	file.write(filedata)

with open('LucasCommits.txt') as f:
    lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    commitLines = [l for l in lines if 'commit' in l]	# only get lines w commit

commitLines.reverse() # commits are new->old : top->bottom
commits = OrderedDict()
for num, line in enumerate(commitLines):
    commits[num+1] = line.split(' ')[-1]

for num, com in commits.items():
    print('----------------------------------------------------------------------------')
    print('Commit {}:	{}'.format(num, com))
    print('Checking out Commit {}'.format(num))
    subprocess.call('git checkout {}'.format(com), shell=True)
    print('SCRAM-ing environment')
    subprocess.call('scram b -j', shell=True)
    # some commits have a hard-coded boolean to use UL histos
    useBool=False
    if num in [4, 8, 9, 10, 11, 12, 13, 14, 15]:
	useBool=True
	print('Setting ULresolutionHistograms = True')
	setULHistoBool()
    print('Running the matrix')
    subprocess.call('./runTheMatrix.sh', shell=True)
    subprocess.call('mv 5.1_TTbar+TTbarFS+HARVESTFS 5.1_TTbar+TTbarFS+HARVESTFS_commit{}'.format(num),shell=True)

    if useBool:
	setULHistoBool(reverse=True)
    
