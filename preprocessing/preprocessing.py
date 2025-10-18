import uproot
import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
import pickle
import sys

in_sample = str(sys.argv[1]) # e.g. ../pythia/output/<file>.root
out_sample = str(sys.argv[2]) # e.g. data/<file>.pkl
out_dir = str(sys.argv[3]) # e.g plots/<Dir Name>

print("Loading Sample into memory...")
with uproot.open(in_sample+":fastjet") as f:
    jet_pt = f["jet_pt"].array()
    jet_eta = f["jet_eta"].array()
    jet_phi = f["jet_phi"].array()
    jet_m = f["jet_m"].array()
    
    #jet_corrJVF = f["jet_corrJVF"].array()
    #jet_RpT = f["jet_RpT"].array()
    jet_Efrac = f["jet_true_Efrac"].array()
    jet_Mfrac = f["jet_true_Mfrac"].array()

    trk_pt = f["trk_pT"].array()
    trk_eta = f["trk_eta"].array()
    trk_phi = f["trk_phi"].array()
    trk_q = f["trk_q"].array()
    trk_d0 = f["trk_d0"].array()
    trk_z0 = f["trk_z0"].array()
    trk_label = f["trk_label"].array()
    trk_ID = f["trk_ID"].array()

    # List of trk_IDs per jet
    jet_trk_association = f["jet_trk_association"].array()

print("Joining jet features...")
jet_feat_list = [jet_pt,jet_eta,jet_phi,jet_m,jet_Efrac,jet_Mfrac]
jet_feat_list = [x[:,:,np.newaxis] for x in jet_feat_list]
jet_feats = ak.concatenate(jet_feat_list, axis=2)
print("\tNum Events: ", len(jet_feats))
print("\tNum Tracks in first event: ", len(jet_feats[0]))
print("\tNum Track Features: ", len(jet_feats[0][0]))

print("Joining track features...")
trk_feat_list = [trk_pt,trk_eta,trk_phi,trk_q,trk_d0,trk_z0,trk_ID,trk_label]
trk_feat_list = [x[:,:,np.newaxis] for x in trk_feat_list]
trk_feats = ak.concatenate(trk_feat_list, axis=2)
print("\tNum Events: ", len(trk_feats))
print("\tNum Tracks in first event: ", len(trk_feats[0]))
print("\tNum Tracks features: ", len(trk_feats[0][0]))

print("Applying Jet Cuts...")
# Apply Jet eta cuts
jet_mask = abs(jet_feats[:,:,1])<4
selected_jets = jet_feats[jet_mask]
jet_trk_association_JET_CUTS = jet_trk_association[jet_mask]

print("Applying Track Cuts...")
# Apply Track cuts
trk_q_cut = trk_feats[:,:,3]!=0          # Skip neutral particles
trk_eta_cut = abs(trk_feats[:,:,1])<4    # Skip forward region
trk_pt_cut = trk_feats[:,:,0]>0.4        # 400MeV Cut
mask = trk_q_cut & trk_eta_cut & trk_pt_cut
selected_tracks_FINAL = trk_feats[mask]

#JET_TRK_ASSOC = np.array([1, 2, 3, 4, 5, 6])
#SEL_TRK = np.array([2, 4, 6, 99, 42])
#mask = np.isin(JET_TRK_ASSOC, SEL_TRK)
#result = JET_TRK_ASSOC[mask]
#print(result) # Result: [2 4 6]

print("Remove dangling IDs in jet_trk_assocation...")
cut_track_mask = []
for event in range(len(jet_trk_association_JET_CUTS)):
    remaining_trk_IDs = ak.to_numpy(selected_tracks_FINAL[event,:,-2])
    event_mask = []
    for jet in range(len(jet_trk_association_JET_CUTS[event])):
        jet_trk_IDs = ak.to_numpy(jet_trk_association_JET_CUTS[event][jet])
        # Get mask to remove dangling jet_trk_associations
        mask = np.isin(jet_trk_IDs, remaining_trk_IDs)
        event_mask.append(mask)
    cut_track_mask.append(event_mask)
cut_track_mask=ak.Array(cut_track_mask)
jet_trk_association_TRK_CUTS = jet_trk_association_JET_CUTS[cut_track_mask]

print("Skip trackless jets...")
# Skip trackless jets!
trackless_jets_mask = (ak.num(jet_trk_association_TRK_CUTS, axis=2)!=0)
selected_jets_FINAL = selected_jets[trackless_jets_mask]
jet_trk_association_FINAL = jet_trk_association_TRK_CUTS[trackless_jets_mask]

print("Convert IDs to idxs...")
for event in range(len(selected_tracks_FINAL)):
    # ID is unique but unordered; Lets create map from ID to index!
    trk_idx_dict = {}
    trk_IDs = selected_tracks_FINAL[event,:,-2]
    for i, ID in enumerate(trk_IDs):
        trk_idx_dict[ID]=i

    # Get index of tracks that belong to each jet
    for jet in range(len(jet_trk_association_FINAL[event])):
        jet_constituent_idxs = [trk_idx_dict[int(trk_ID)] for trk_ID in jet_trk_association_FINAL[event,jet]]

print("Dump to pickle file...")

data_dict ={"jets": selected_jets_FINAL, "jet_trk_idx": jet_constituent_idxs, "trks": selected_tracks_FINAL}

with open(out_sample, "wb") as f:
    pickle.dump(data_dict, f)

print("Validation Plots...")

Efrac_cut=0.5

sig = selected_jets_FINAL[:,:,-2]>Efrac_cut
bkg = ~sig

isHS = selected_tracks_FINAL[:,:,-1]==-1
isPU = ~isHS

plt.figure()
plt.title("Jet Efrac")
plt.hist(ak.ravel(selected_jets_FINAL[:,:,-2][sig]),histtype='step',label=f'Efrac>{Efrac_cut}',color='r',bins=30,range=(0,1))
plt.hist(ak.ravel(selected_jets_FINAL[:,:,-2][bkg]),histtype='step',label=f'Efrac<={Efrac_cut}',color='b',bins=30,range=(0,1))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Jet_Efrac.png")
#plt.show()

plt.figure()
plt.title("Jet Mfrac")
plt.hist(ak.ravel(selected_jets_FINAL[:,:,-1][sig]),histtype='step',label=f'Efrac>{Efrac_cut}',color='r',bins=30,range=(0,1))
plt.hist(ak.ravel(selected_jets_FINAL[:,:,-1][bkg]),histtype='step',label=f'Efrac<={Efrac_cut}',color='b',bins=30,range=(0,1))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Jet_Mfrac.png")
#plt.show()

plt.figure()
plt.title("Trk Vertex Label")
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,-1][isHS]),histtype='step',label='isHS',color='r',bins=40,range=(-1,40))
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,-1][isPU]),histtype='step',label='isPU',color='b',bins=40,range=(-1,40))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Trk_Label.png")
#plt.show()

plt.figure()
plt.title("Jet pT")
plt.hist(ak.ravel(selected_jets_FINAL[:,:,0][sig]),histtype='step',label=f'Efrac>{Efrac_cut}',color='r',bins=40,range=(0,400))
plt.hist(ak.ravel(selected_jets_FINAL[:,:,0][bkg]),histtype='step',label=f'Efrac<={Efrac_cut}',color='b',bins=40,range=(0,400))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Jet_pT.png")
#plt.show()

plt.figure()
plt.title("Jet eta")
plt.hist(ak.ravel(selected_jets_FINAL[:,:,1][sig]),histtype='step',label=f'Efrac>{Efrac_cut}',color='r',bins=40,range=(-4,4))
plt.hist(ak.ravel(selected_jets_FINAL[:,:,1][bkg]),histtype='step',label=f'Efrac<={Efrac_cut}',color='b',bins=40,range=(-4,4))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Jet_eta.png")
#plt.show()

plt.figure()
plt.title("Jet phi")
plt.hist(ak.ravel(selected_jets_FINAL[:,:,2][sig]),histtype='step',label=f'Efrac>{Efrac_cut}',color='r',bins=40,range=(0,6.3))
plt.hist(ak.ravel(selected_jets_FINAL[:,:,2][bkg]),histtype='step',label=f'Efrac<={Efrac_cut}',color='b',bins=40,range=(0,6.3))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Jet_phi.png")
#plt.show()

plt.figure()
plt.title("Jet mass")
plt.hist(ak.ravel(selected_jets_FINAL[:,:,3][sig]),histtype='step',label=f'Efrac>{Efrac_cut}',color='r',bins=40,range=(0,200))
plt.hist(ak.ravel(selected_jets_FINAL[:,:,3][bkg]),histtype='step',label=f'Efrac<={Efrac_cut}',color='b',bins=40,range=(0,200))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Jet_mass.png")
#plt.show()

plt.figure()
plt.title("Track pT")
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,0][isHS]),histtype='step',label="isHS",color='r',bins=40,range=(0,150))
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,0][isPU]),histtype='step',label="isHS",color='b',bins=40,range=(0,150))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Track_pT.png")
#plt.show()

plt.figure()
plt.title("Track eta")
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,1][isHS]),histtype='step',label="isHS",color='r',bins=40,range=(-4,4))
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,1][isPU]),histtype='step',label="isHS",color='b',bins=40,range=(-4,4))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Track_eta.png")
#plt.show()

plt.figure()
plt.title("Track phi")
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,2][isHS]),histtype='step',label="isHS",color='r',bins=40,range=(-3.14,3.14))
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,2][isPU]),histtype='step',label="isHS",color='b',bins=40,range=(-3.14,3.14))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Track_phi.png")
#plt.show()

plt.figure()
plt.title("Track q")
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,3][isHS]),histtype='step',label="isHS",color='r',bins=40,range=(-1,1))
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,3][isPU]),histtype='step',label="isHS",color='b',bins=40,range=(-1,1))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Track_q.png")
#plt.show()

plt.figure()
plt.title("Track d0")
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,4][isHS]),histtype='step',label="isHS",color='r',bins=40,range=(-300,300))
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,4][isPU]),histtype='step',label="isHS",color='b',bins=40,range=(-300,300))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Track_d0.png")
#plt.show()

plt.figure()
plt.title("Track z0")
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,5][isHS]),histtype='step',label="isHS",color='r',bins=40,range=(-2000,2000))
plt.hist(ak.ravel(selected_tracks_FINAL[:,:,5][isPU]),histtype='step',label="isHS",color='b',bins=40,range=(-2000,2000))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Track_z0.png")
#plt.show()

print("Done!")
