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

num_events = len(AE_input)

train_split = int(0.7*num_events)  # 70% train
test_split = int(0.75*num_events)  #  5% val + 25% test

X_train, y_train = [AE_input[:train_split], AE_output[:train_split]]
X_val, y_val = [AE_input[train_split:test_split], AE_output[train_split:test_split]]
X_test, y_test = [AE_input[test_split:], AE_output[test_split:]]

data_dict = {
    "X_train": X_train,
    "y_train": y_train,
    "X_val": X_val,
    "y_val": y_val,
    "X_test": X_test,
    "y_test": y_test,
}

with open(out_dir_data+"/data_combined.pkl","wb") as f:
    pickle.dump(data_dict, f)
print("\tDone Combining Runs!")
