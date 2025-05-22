import uproot
import awkward as ak
import numpy as np
import torch
import sys
import pickle

pythia_tag1 = str(sys.argv[1])
pythia_tag2 = str(sys.argv[2])
run = str(sys.argv[3])
out_dir = str(sys.argv[4])

AE_input_path = "../pythia/WS_"+pythia_tag1+"/data/dataset_showered_run_"+run+".root"
AE_output_path = "../pythia/WS_Showered_mu0/data/dataset_showered_run_"+run+".root"

def get_data(path):
    with uproot.open(path+":fastjet") as f:
        # Read each feat into awkward array
        trk_pT = f['trk_pT'].array()
        trk_eta = f['trk_eta'].array()
        trk_phi = f['trk_phi'].array()
        trk_q = f['trk_q'].array()
        trk_d0 = f['trk_d0'].array()
        trk_z0 = f['trk_z0'].array()
        trk_label = f['trk_label'].array()

    # Store akward arrays in a dictionary
    feats = {'pT': trk_pT,
             'eta': trk_eta,
             'phi': trk_phi,
             'q': trk_q,
             'd0': trk_d0,
             'z0': trk_z0,
             'label': trk_label,                   
            }
    return feats

AE_input_dict = get_data(AE_input_path)
AE_output_dict = get_data(AE_output_path)

num_events = len(AE_input_dict['pT'])

tensor_AE_output = []
tensor_AE_input = []

combined_AE_input = [x[:,:,np.newaxis] for x in AE_input_dict.values()]
combined_AE_input = ak.concatenate(combined_AE_input, axis=2)

feats = ['pT','eta','phi','q','d0','z0','label']

for event in range(num_events):
    if event%1==0:
        print("\tProcessing: ", event, " / ", num_events, end="\r")
    padded_feat_list = []
    max_tracks = len(combined_AE_input[event])
    for feat in feats:
        padded_feat = ak.fill_none(ak.pad_none(AE_output_dict[feat][event], max_tracks, axis=0), 0)
        padded_feat_list.append(padded_feat)
    padded_feat_list = [x[:,np.newaxis] for x in padded_feat_list]
    padded_feat_list = ak.concatenate(padded_feat_list, axis=1)
    
    tensor_AE_output.append(torch.Tensor(padded_feat_list))
    tensor_AE_input.append(torch.Tensor(combined_AE_input[event]))
    
print("\tProcessing: ", num_events, " / ", num_events)

tensor_dict = {"AE_input": tensor_AE_input,
               "AE_output": tensor_AE_output,
              }

with open(out_dir+"/preprocessed_"+run+".pkl","wb") as f:
    pickle.dump(tensor_dict, f)
