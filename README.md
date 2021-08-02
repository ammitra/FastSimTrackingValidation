Automation for FastSim tracking validation (though useful beyond just tracking). Runs generation (AOD, DQM), tracking validation, MiniAOD, b tagging validation, and NanoAOD.
Additionally analysis level processing can be added.

Instructions for setup in CMSSW (tested in CMSSW_10_6_14).
```
cmsrel CMSSW_10_6_14
cd CMSSW_10_6_14/src
cmsenv
python -m virtualenv fsv_env
source fsv_env/bin/activate # or applicable activation script
git clone https://github.com/lcorcodilos/FastSimTrackingValidation.git
git clone https://github.com/cms-btv-pog/Validation-Tools.git
pip install -e FastSimTrackingValidation/
cp FastSimTrackingValidation/extras/validation-tools_setup.py Validation-Tools/setup.py
pip install -e Validation-Tools/
```

The primary script to run workflows is `run.py`. The script takes several options
which will control the multi-step workflow. These options can be provided via the command line
or via a "payload" in JSON format with entries that correspond to the command line options.
The payload is specified with command line option `-c`.
Any options that are in the payload and not covered by `run.py` are passed to cmsDriver so that this payload can
also specify the cmsDriver setup.

One should also always specify a `--tag` to uniquely identify the run so that the results
won't be overwritten and so the results can be identified uniquely.

An example payload for a 2018UL ttbar workflow with no pileup:
```json
{
    "dir":"../../BaseFastSim",
    "steps":"AOD,TRACKVAL,BTAGVAL,MINIAOD,NANOAOD",
    "crab":false,
    "cfi":"TTbar_13TeV_TuneCUETP8M1_cfi",
    "cmssw":"CMSSW_10_6_4",
    "conditions": "auto:phase1_2018_realistic",
    "era": "Run2_2018_FastSim",
    "beamspot": "Realistic25ns13TeVEarly2018Collision"
}
```

An example payload for a 2018UL ttbar workflow **with** pileup:
```json
{
    "dir":"../../BaseFastSim",
    "steps":"AOD,TRACKVAL,BTAGVAL,MINIAOD,NANOAOD",
    "crab":false,
    "cfi":"TTbar_13TeV_TuneCUETP8M1_cfi",
    "cmssw":"CMSSW_10_6_4",
    "conditions": "auto:phase1_2018_realistic",
    "era": "Run2_2018_FastSim",
    "beamspot": "Realistic25ns13TeVEarly2018Collision",
    "pileup_input":"das:/RelValFS_PREMIXUP18_PU50/CMSSW_10_6_4-PU25ns_106X_upgrade2018_realistic_v9_FastSim-v1/PREMIX",
    "datamix": "PreMix",
    "procModifiers": "premix_stage2"
}
```

An example command to use one of these:
```
python FastSimTrackingValidation/run.py -c payload_nopu.json --tag=Ttbar2018NoPU
```

Note that the `dir` option is a relative path to an existing directory
which houses a `cmssw` area (release specified by the `cmssw` option)
which is prepared to generate events.
The `dir` and `cmssw` are separated in the case that one `dir` holds multiple
CMSSW releases to be tested.

For either of the above example payloads, the `run.py` will change to `../../BaseFastSim/CMSSW_10_6_4/src`
and run the `steps` specified using `cmsDriver` commands with the options specified in the payload.
Default options are specified so be sure to check the cmsRun config outputs to check that the final
commands used match what you intended to run.

### Generating with custom changes

In order to generate events with custom private changes made to the CMSSW code base,
one must first create the modified CMSSW release area and scram it before attempting to use
`run.py`. One can also use the `run.py` `SCRAM` option to always scram ahead of time but
it's recommend you do this manually so that you don't forget!

## CRAB functionality
The `crab` option will use the CRABAPI to submit crab jobs. The default crab config setup
can be modified in `common.fastsimTrackingHelpers.MakeCrabConfig`.
This has worked consistently for me (Lucas) but is overkill for generating O(1000) events
(which takes about an hour for all steps from AOD to NanoAOD).
There's no reason to believe it won't work out of the box for other users but no one
else has ever tested it (though there's nothing hard-coded with
my credentials beyond the default `storageSite` option value of "T3_US_FNALLPC").

Note that even if you are not using CRAB, you will be required to run `source /cvmfs/cms.cern.ch/common/crab-setup.sh`
at least once so that the API can be imported still. If you forget this, there will be a message explaining this
and reminding you of the command.

## Web scraping for RelVals
Finding existing RelVels is relatively frustrating. Most annoying is that the existing HyperNews
has O(100,000) entries which causes browsers to slow down and makes it very hard to search
for a relevant campaign. Additionally, it's not clear from the thread/message title what
processes were simulated - these are stored on different pages linked to by the actual HN message.

To make this simpler, there is a simple web scraper to automate getting this information.
The RelVel HN HTML is downloaded in `scraping/relvalHN.html` but should be updated.
To do so, add your HN login credentials to the `UserID` and `Password` variables in `scraping/HNinfo.py`.
Note this is unencrypted so 
# DO NOT COMMIT CHANGES WITH YOUR USERID AND PASSWORD TO GITHUB

Once this information is added, one can run the following steps
```
cd scraping/
python update_relvalHN.py
cd ../
```

You can check it worked by checking `relvalHN.html` is filled.
If it shows any authentication error information, then your `UserID` and `Password`
are incorrect.

To start looking for RelVals, use `scraper/HNscaper.py` in conjunction with a `grep` of `relvalHN.html.`
Note that this will also require the `scraping/HNinfo.py` changes for the `UserID` and `Password` variables
as described in the step above.

```
grep '<text in post title>' scraper/relvalHN.html | python HNscraper.py --find "myString"
```

This will take a little bit of knowledge to get working correctly. The string argument to `grep`
is a string that you'd like to find in the actual HN post title. For example, a CMSSW version
is usually useful here.

The `--find` argument to HNscraper.py is the string to search on the pages nested in the HN post
(note, this means the actual pages linked to in the HN post, not the HN post itself). It may be 
useful to click through one example to figure out what to search for but usually a physics dataset
process name like "TTbar" or "Zprime" is suitable.

The final output will be a print out of urls to pages that match both the CMSSW version and dataset (in this
example, at least).