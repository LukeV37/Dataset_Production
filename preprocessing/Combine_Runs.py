import pickle
import sys
import awkward as ak

num_runs = int(sys.argv[1])
out_dir_data= str(sys.argv[2])

jet_feats = []
jet_trk_IDs = []
trk_feats = []

def get_data(out_dir_data,run):
    with open(out_dir_data+"/data/dataset_preprocessed_run_"+run+".pkl","rb") as f:
        data_dict = pickle.load(f)
    return ak.to_list(data_dict["jets"]), ak.to_list(data_dict["jet_trk_IDs"]), ak.to_list(data_dict["trks"])

for i in range(num_runs):
    print("\tCombining Batch ", i)
    jet_data, jet_trk_data, all_trk_data = get_data(out_dir_data,str(i))
    jet_feats+=jet_data
    jet_trk_IDs+=jet_trk_data
    trk_feats+=all_trk_data

data_dict = {
    "jets": ak.Array(jet_feats),
    "jet_trk_IDs": ak.Array(jet_trk_IDs),
    "trks": ak.Array(trk_feats),
}

with open(out_dir_data+"/data_combined.pkl","wb") as f:
    pickle.dump(data_dict, f)
print("\tDone Combining Runs!")
