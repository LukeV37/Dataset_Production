# filename: preprocess_events.py

import pickle
import numpy as np
import os
from typing import Tuple, Optional

def preprocess_and_split_events(
    pickle_path: str,
    output_dir: str,
    dataset_name: str,
    seed: int = 42,
    split_ratios: Tuple[float, float, float] = (0.8, 0.1, 0.1),
    subset_size: Optional[int] = None
):
    """
    Loads raw event data, shuffles all event indices, optionally selects a
    random subset, and then splits that set into train/validation/test files.
    """
    print(f"Loading raw event data from {pickle_path}...")
    with open(pickle_path, "rb") as f:
        data_dict = pickle.load(f)

    # Extract all necessary data components from the dictionary
    jet_events_ak = data_dict["jets"]
    jet_track_events_ak = data_dict["jet_trk_IDs"]
    all_track_events_ak = data_dict["trks"]

    num_events_total = len(jet_events_ak)
    print(f"Found {num_events_total} total events in file.")

    # --- Event-level Shuffle ---
    # Shuffle all event indices FIRST to ensure a random sample
    print(f"Shuffling all {num_events_total} event indices with seed {seed}...")
    np.random.seed(seed)
    all_shuffled_indices = np.random.permutation(num_events_total)

    # --- Select a random subset after shuffling ---
    if subset_size is not None:
        if subset_size > num_events_total:
            print(f"Warning: Requested subset_size {subset_size}, but only {num_events_total} are available.")
            subset_size = num_events_total
        
        print(f"--- Selecting a random subset of {subset_size} events for processing ---")
        # Take the first N indices from the fully shuffled list
        event_indices_to_split = all_shuffled_indices[:subset_size]
    else:
        # If not taking a subset, use all the shuffled indices
        print(f"--- Processing all {num_events_total} events ---")
        event_indices_to_split = all_shuffled_indices
    
    # The number of events we are splitting is now the size of our selected subset
    num_events_to_split = len(event_indices_to_split)

    # --- Calculate split points based on the subset size ---
    train_end = int(num_events_to_split * split_ratios[0])
    val_end = train_end + int(num_events_to_split * split_ratios[1])

    # Split the *subset* of indices
    train_indices = event_indices_to_split[:train_end]
    val_indices = event_indices_to_split[train_end:val_end]
    test_indices = event_indices_to_split[val_end:]
    
    os.makedirs(output_dir, exist_ok=True)

    # Helper function to save each data split
    def save_split(name, indices):
        # We slice from the ORIGINAL, FULL awkward arrays using the final indices
        split_jets = jet_events_ak[indices]
        split_jet_tracks = jet_track_events_ak[indices]
        split_all_tracks = all_track_events_ak[indices]
        
        data_to_save = (split_jets, split_jet_tracks, split_all_tracks)
        output_path = os.path.join(output_dir, f"{dataset_name}_{name}_seed_{seed}.pkl")
        
        print(f"Saving {len(split_jets)} events for '{name}' set to {output_path}...")
        with open(output_path, "wb") as f:
            pickle.dump(data_to_save, f)

    # Save each of the three splits
    save_split('train', train_indices)
    save_split('validation', val_indices)
    save_split('test', test_indices)

    print("\nEvent-based pre-processing and splitting complete for Phase 2.")

if __name__ == '__main__':
    # --- Flag to create the 1000-event subset for hyperparameter tuning ---
    # CREATE_SUBSET = True
    CREATE_SUBSET = False
    
    PROCESSED_DATA_DIR = "/home/lvaughan/Work/Dataset_Production/preprocessing/results"
    RANDOM_SEED = 42
    SPLIT_RATIOS = (0.8, 0.1, 0.1) # Will be applied to the 1000 events
    
    # --- Logic to set parameters based on the flag ---
    subset_size_to_process = None
    # dataset_name = "mu60_10k_events" # Default name for 10k events
    dataset_name = "data_combined" # Default name for 10k events
    
    # --- Configuration ---
    # RAW_PICKLE_FILE = f"/home/rakib/HyperGraph-PileUp/data/raw_data/{dataset_name}_data.pkl"
    RAW_PICKLE_FILE = f"/home/lvaughan/Work/Dataset_Production/preprocessing/WS_Preprocessed_ttbar_semiLep_mu60_minJetpT25/{dataset_name}.pkl"
    
    if CREATE_SUBSET:
        subset_size_to_process = 1000 # Select a random 1000 events
        # dataset_name = "mu60_1k_events" # New name for the 1k subset
        dataset_name = "mu200_1k_events" # New name for the 1k subset
        print(f"--- RUNNING IN SUBSET MODE (Randomly selecting {subset_size_to_process} events) ---")
    
    preprocess_and_split_events(
        pickle_path=RAW_PICKLE_FILE,
        output_dir=PROCESSED_DATA_DIR,
        dataset_name=dataset_name, # Use the dynamic name
        seed=RANDOM_SEED,
        split_ratios=SPLIT_RATIOS,
        subset_size=subset_size_to_process # Pass the new parameter
    )
