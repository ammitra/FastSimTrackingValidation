Automation for fast sim tracking validation jobs. Runs generation (AOD, DQM), tracking validation, MiniAOD, b tagging validation, and NanoAOD.

It's recommended to create a virtual environment for setup in a CMSSW release (tested in CMSSW_10_6_14) so you can use pip.
```
virtualenv fsv_env
source fsv_env/bin/activate # or applicable activation script
git clone https://github.com/lcorcodilos/FastSimTrackingValidation.git
git clone https://github.com/cms-btv-pog/Validation-Tools.git
pip install -e FastSimTrackingValidation/
cp FastSimTrackingValidation/extras/validation-tools_setup.py Validation-Tools/setup.py
pip install -e Validation-Tools/
```