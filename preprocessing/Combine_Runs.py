import pickle
import sys
import awkward as ak

num_runs = int(sys.argv[1])
out_dir_data= str(sys.argv[2])

jet_tensor = []
jet_trk_tensor = []
all_trk_tensor = []

def get_data(out_dir_data,run):
    with open(out_dir_data+"/data/dataset_preprocessed_run_"+run+".pkl","rb") as f:
        data_dict = pickle.load(f)
    return ak.to_list(data_dict["jets"]), ak.to_list(data_dict["jet_trks"]), ak.to_list(data_dict["all_trks"])

for i in range(num_runs):
    print("\tCombining Batch ", i)
    jet_data, jet_trk_data, all_trk_data = get_data(out_dir_data,str(i))
    jet_tensor+=jet_data
    jet_trk_tensor+=jet_trk_data
    all_trk_tensor+=all_trk_data

data_dict = {
    "jets": ak.Array(jet_tensor),
    "jet_trks": ak.Array(jet_trk_tensor),
    "all_trks": ak.Array(all_trk_tensor),
}

with open(out_dir_data+"/data_combined.pkl","wb") as f:
    pickle.dump(data_dict, f)
print("\tDone Combining Runs!")
