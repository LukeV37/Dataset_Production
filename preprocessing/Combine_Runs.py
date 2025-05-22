import pickle
import sys

num_runs = int(sys.argv[1])
out_dir_data= str(sys.argv[2])

AE_input = []
AE_output = []

def get_data(out_dir_data,run):
    with open(out_dir_data+"/run_"+run+"/preprocessed_"+run+".pkl","rb") as f:
        data_dict = pickle.load(f)
    return data_dict["AE_input"], data_dict["AE_output"]

for i in range(num_runs):
    print("\tCombining Batch ", i)
    in_data, out_data = get_data(out_dir_data,str(i))
    AE_input+=in_data
    AE_output+=out_data

data_dict = {
    "AE_input": AE_input,
    "AE_output": AE_output,
}

with open(out_dir_data+"/data_combined.pkl","wb") as f:
    pickle.dump(data_dict, f)
print("\tDone Combining Runs!")
