import uproot
import numpy as np
import matplotlib.pyplot as plt
import awkward as ak
import pickle
import sys

import torch
import torch.nn.functional as F

in_sample = str(sys.argv[1]) # e.g. ../pythia/output/<file>.root
out_sample = str(sys.argv[2]) # e.g. data/<file>.pkl
out_dir = str(sys.argv[3]) # e.g plots/<Dir Name>

print("Loading Sample into memory...")
with uproot.open(in_sample+":fastjet") as f:
    jet_pt = f["jet_pt"].array()
    jet_eta = f["jet_eta"].array()
    jet_phi = f["jet_phi"].array()
    jet_corrJVF = f["jet_corrJVF"].array()
    jet_RpT = f["jet_RpT"].array()
    jet_m = f["jet_m"].array()
    trk_pt = f["trk_jet_pT"].array()
    trk_eta = f["trk_jet_eta"].array()
    trk_phi = f["trk_jet_phi"].array()
    trk_q = f["trk_jet_q"].array()
    trk_d0 = f["trk_jet_d0"].array()
    trk_z0 = f["trk_jet_z0"].array()
    trk_label = f["trk_jet_label"].array()
    all_trk_pt = f["trk_pT"].array()
    all_trk_eta = f["trk_eta"].array()
    all_trk_phi = f["trk_phi"].array()
    all_trk_q = f["trk_q"].array()
    all_trk_d0 = f["trk_d0"].array()
    all_trk_z0 = f["trk_z0"].array()
    all_trk_label = f["trk_label"].array()
    jet_Efrac = f["jet_true_Efrac"].array()
    jet_Mfrac = f["jet_true_Mfrac"].array()

print("Joining jet features...")
jet_feat_list = [jet_pt,jet_eta,jet_phi,jet_m,jet_Efrac,jet_Mfrac]
jet_feat_list = [x[:,:,np.newaxis] for x in jet_feat_list]
jet_feats = ak.concatenate(jet_feat_list, axis=2)
print("\tNum Events: ", len(jet_feats))
print("\tNum Jets in first event: ", len(jet_feats[0]))
print("\tNum Jet Features: ", len(jet_feats[0][0]))

print("Joining track features...")
trk_feat_list = [trk_pt,trk_eta,trk_phi,trk_q,trk_d0,trk_z0,trk_label]
trk_feat_list = [x[:,:,:,np.newaxis] for x in trk_feat_list]
trk_feats = ak.concatenate(trk_feat_list, axis=3)
print("\tNum Events: ", len(trk_feats))
print("\tNum Jets in first event: ", len(trk_feats[0]))
print("\tNum Tracks in first event first jet: ", len(trk_feats[0][0]))
print("\tNum Tracks features: ", len(trk_feats[0][0][0]))

print("Joining all track features...")
all_trk_feat_list = [all_trk_pt,all_trk_eta,all_trk_phi,all_trk_q,all_trk_d0,all_trk_z0,all_trk_label]
all_trk_feat_list = [x[:,:,np.newaxis] for x in all_trk_feat_list]
all_trk_feats = ak.concatenate(all_trk_feat_list, axis=2)
print("\tNum Events: ", len(all_trk_feats))
print("\tNum Tracks in first event: ", len(trk_feats[0]))
print("\tNum Tracks features: ", len(trk_feats[0][0]))

print("Shuffling Events...")
# Shuffle events
p = np.random.permutation(len(jet_feats))
jet_feats = jet_feats[p]
trk_feats = trk_feats[p]

print("Applying Cuts...")
# Apply Jet cuts
jet_mask = abs(jet_feats[:,:,1])<4
selected_jets = jet_feats[jet_mask]
selected_tracks = trk_feats[jet_mask]

# Apply Track cuts
trk_q_cut = selected_tracks[:,:,:,3]!=0            # Skip neutral particles
trk_eta_cut = abs(selected_tracks[:,:,:,1])<4.5    # Skip forward region
trk_pt_cut = selected_tracks[:,:,:,0]>0.4          # 400MeV Cut
mask = trk_q_cut & trk_eta_cut & trk_pt_cut
selected_tracks = selected_tracks[mask]

# Skip trackless jets!
trackless_jets_mask = (ak.num(selected_tracks, axis=2)!=0)
selected_jets = selected_jets[trackless_jets_mask]
selected_tracks = selected_tracks[trackless_jets_mask]

# Apply All Track cuts
all_trk_q_cut = all_trk_feats[:,:,3]!=0            # Skip neutral particles
all_trk_eta_cut = abs(all_trk_feats[:,:,1])<4.5    # Skip forward region
all_trk_pt_cut = all_trk_feats[:,:,0]>0.4          # 400MeV Cut
mask = all_trk_q_cut & all_trk_eta_cut & all_trk_pt_cut
all_tracks = all_trk_feats[mask]

sig = selected_jets[:,:,-2]>0.5
bkg = ~sig

plt.figure()
plt.title("Jet Efrac")
plt.hist(ak.ravel(selected_jets[:,:,-2][sig]),histtype='step',label='HS',bins=30,range=(0,1))
plt.hist(ak.ravel(selected_jets[:,:,-2][bkg]),histtype='step',label='PU',bins=30,range=(0,1))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Jet_Efrac.png")
#plt.show()

plt.figure()
plt.title("Jet Mfrac")
plt.hist(ak.ravel(selected_jets[:,:,-1][sig]),histtype='step',label='HS',bins=30,range=(0,1))
plt.hist(ak.ravel(selected_jets[:,:,-1][bkg]),histtype='step',label='PU',bins=30,range=(0,1))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Jet_Mfrac.png")
#plt.show()

plt.figure()
plt.title("Trk Vertex Label")
plt.hist(ak.ravel(selected_tracks[:,:,:,-1][sig]),histtype='step',label='HS',bins=41,range=(-1,40))
plt.hist(ak.ravel(selected_tracks[:,:,:,-1][bkg]),histtype='step',label='PU',bins=41,range=(-1,40))
plt.yscale('log')
plt.legend()
plt.savefig(out_dir+"/Trk_Label.png")
plt.show()

"""
print("Padding Tracks to common length...")
num_events = len(selected_jets)
jet_trk_list=[]
for event in range(num_events):
    if event%1==0:
        print("\tProcessing: ", event, " / ", num_events, end="\r")
    num_trks = ak.num(selected_tracks[event], axis=1)
    max_num_trks = ak.max(num_trks)
    trk_list = []
    num_jets = len(selected_jets[event])
    for jet in range(num_jets):
        tracks = torch.Tensor(selected_tracks[event][jet,:])
        pad = (0,0,0,max_num_trks-len(tracks))
        tracks = F.pad(tracks,pad)
        trk_list.append(torch.unsqueeze(tracks,dim=0))
    tracks = torch.cat(trk_list,dim=0)
    jet_trk_list.append(tracks)
print("\tProcessing: ", num_events, " / ", num_events)
"""
    
print("Nested Tensor Jets")
selected_jets = torch.nested.nested_tensor(ak.to_list(selected_jets), layout=torch.jagged)
print("Nested Tensor Jets-Trks")
selected_jet_trks = selected_tracks
print("Nested Tensor All-Trks")
all_trks = torch.nested.nested_tensor(ak.to_list(all_tracks), layout=torch.jagged)

data_dict ={"jets": selected_jets, "jet_trks": selected_jet_trks, "all_trks": all_trks}

with open(out_sample, "wb") as f:
    pickle.dump(data_dict, f)

print("Done!")
