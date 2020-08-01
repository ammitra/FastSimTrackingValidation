import sys, ROOT
from Analyzer import analyzer,HistGroup
from Tools.Common import CompileCpp,GetHistBinningTuple

addVectItems = '''
#include<algorithm> 
using namespace ROOT::VecOps;

template <typename T>
RVec<T> FillEmptySlots(int length, RVec<T>& v) {
    RVec<T> out(length, -1234);
    int loopsize = v.size() < length? v.size() : length;
    for (int i; i< loopsize; i++){
        out[i] = v[i];
    }

    return out;
}
'''

binning_min = {
    'eta':-3,
    'CMVA':-1,
    'phi':-3.1415
}

def NanoValidation(filename,outfilename):
    a = analyzer(filename)
    CompileCpp(addVectItems)

    maxFatJets = 2#int(a.GetActiveNode().DataFrame.Max("nFatJet").GetValue())
    maxJets = 4#int(a.GetActiveNode().DataFrame.Max("nJet").GetValue())

    # These are what we'll draw out
    colsToDraw = []
    # Get the FatJet and Jet column names
    colsFatJet = [cname for cname in a.GetActiveNode().DataFrame.GetColumnNames() if cname.find('FatJet_') == 0 and '.' not in cname]
    colsJet = [cname for cname in a.GetActiveNode().DataFrame.GetColumnNames() if cname.find('Jet_') == 0 and '.' not in cname and 'cleanmask' not in cname]

    # For each the FatJet and Jet columns, fill out the vectors so they always have max entries
    for c in colsFatJet:
        vect_name = '%s_filled'%(c)
        a.Define(vect_name,'FillEmptySlots(%s, %s)'%(maxFatJets, c))
        for i in range(maxFatJets):
            newname = '%s_%s'%(vect_name,i)
            item_name = vect_name+'[%s]'%i
            a.Define(newname,item_name)
            colsToDraw.append(newname)

    for c in colsJet:
        vect_name = '%s_filled'%(c)
        a.Define('%s_filled'%(c),'FillEmptySlots(%s, %s)'%(maxJets, c))
        for i in range(maxJets):
            newname = '%s_%s'%(vect_name,i)
            item_name = vect_name+'[%s]'%i
            a.Define(newname,item_name)
            colsToDraw.append(newname)

    # Set weight to 0 if value is -10 (manufactured value)
    for c in colsToDraw:
        a.Define(c.replace('_filled','_weight'),c+' != -1234 ? 1 : 0')

    # Make a hist group
    hg = HistGroup('outs')
    bins = {}
    # Need consistent binning so do get 0th element histograms first and then
    # steal binning for the rest
    for c in colsToDraw:
        if '_filled_0' in c:
            # Check if a bin min is defined
            bin_min = 0
            for kbin in binning_min.keys():
                if kbin in c: bin_min = binning_min[kbin]
        
            h_pointer = a.GetActiveNode().DataFrame.Histo1D(c)
            h = h_pointer.GetValue()
            bins[c.replace('_0','')], dimension = GetHistBinningTuple(h)
            bins[c.replace('_0','')] = (50, max(bin_min, bins[c.replace('_0','')][1]) if 'eta' not in c else -1*bins[c.replace('_0','')][2], bins[c.replace('_0','')][2])
            hg.Add(c,h_pointer)
    # Now draw the rest
    for c in colsToDraw:
        # if '_filled_0' in c: continue
        binningTuple = (c,c)+bins[c[:c.find('filled_')+len('filled')]] #only works if max*Jet < 10
        hg.Add(c, a.GetActiveNode().DataFrame.Histo1D(binningTuple,c,c.replace('filled','weight')))

    # Finally, hadd 0th [1,N]th and write
    outFile = ROOT.TFile.Open(outfilename,'RECREATE')
    outFile.cd()
    for c in colsFatJet+colsJet:
        out_h = hg[c+'_filled_0'].Clone(c)
        thismax = maxFatJets if c in colsFatJet else maxJets
        for i in range(1,thismax):
            out_h.Add(hg[c+'_filled_'+str(i)].GetValue())

        out_h.Write()

    outFile.Close()

if __name__ == '__main__':
    NanoValidation(sys.argv[1],sys.argv[2])
    
    