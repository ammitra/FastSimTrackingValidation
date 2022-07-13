This is Lucas' cmssw fork. 

1) Run `getCommits.py` to get the commits (in order) that Lucas made to the FastSimulation 

2) Run `git checkout <commit>` to move to that commit

3) Run `runTheMatrix.py -l 5.1 -j 8 --command='-n 1000'` to run the matrix 

4) rename the output dir with `_commit#`

5) run the comparison script in `CMSSW_10_6_14/src`
