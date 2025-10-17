#include <TTree.h>
#include <TFile.h>

#include <vector>
using std::vector;

#include <iostream>
using std::cout;
using std::endl;

#include <TLorentzVector.h>

#include <cmath>

int main(int argc, char *argv[])
{

  char *name = argv[1];

  // the existing tree will be updated!
  TFile* ff = new TFile(TString(name), "update");

  // fastjet ntuple
  TTree* treefj = (TTree*)ff->Get("fastjet");

  // new branches to add
  vector<float> jet_true_Efrac;
  vector<float> jet_true_Mfrac;
  TBranch* b_jet_true_Efrac = treefj->Branch("jet_true_Efrac", &jet_true_Efrac);
  TBranch* b_jet_true_Mfrac = treefj->Branch("jet_true_Mfrac", &jet_true_Mfrac);

  // existing branches to use
  vector<float>* jet_pT;
  vector<float>* trk_pT;
  vector<float>* trk_eta;
  vector<float>* trk_phi;
  vector<int>* trk_label;
  vector<vector<int>>* jet_trk_association;

  treefj->SetBranchAddress("jet_pt", &jet_pT);
  treefj->SetBranchAddress("trk_pT", &trk_pT);
  treefj->SetBranchAddress("trk_eta", &trk_eta);
  treefj->SetBranchAddress("trk_phi", &trk_phi);
  treefj->SetBranchAddress("trk_label", &trk_label);
  treefj->SetBranchAddress("jet_trk_association", &jet_trk_association);

  // loop over fastjet
  int nevfj = treefj->GetEntries();
  cout << "fastjet entries: " << nevfj << endl;
  for (int ievfj = 0; ievfj<nevfj; ++ievfj) {
    if (ievfj%1000==0) { cout << ievfj << '\r'; cout.flush(); }

    jet_pT = 0;
    trk_pT = 0;
    trk_eta = 0;
    trk_phi = 0;
    trk_label = 0;
    jet_trk_association = 0;

    treefj->GetEntry(ievfj);

    // loop over jets
    int njet = jet_pT->size();
    jet_true_Efrac = vector<float>(njet);
    jet_true_Mfrac = vector<float>(njet);
    for (int ijet = 0; ijet<njet; ++ijet) {
      int ntr = (*jet_trk_association)[ijet].size();
      if (ntr<=0) continue;
      TLorentzVector vtot, vhs;
      for (int itr = 0; itr<ntr; ++itr) {
        int trk_idx = (*jet_trk_association)[ijet][itr];
        TLorentzVector v; v.SetPtEtaPhiM((*trk_pT)[trk_idx],(*trk_eta)[trk_idx],(*trk_phi)[trk_idx],0.0001);
        vtot += v;
        if ((*trk_label)[trk_idx]==-1) {
          vhs += v;
        }
      }
      double true_Efrac = vtot.E(); if (true_Efrac>0) true_Efrac = vhs.E()/true_Efrac;
      double true_Mfrac = vtot.M(); if (true_Mfrac>0) true_Mfrac = vhs.M()/true_Mfrac;
      cout << true_Efrac << true_Mfrac << endl;
      jet_true_Efrac[ijet] = true_Efrac;
      jet_true_Mfrac[ijet] = true_Mfrac;
    }
    b_jet_true_Efrac->Fill();
    b_jet_true_Mfrac->Fill();
  }

  // save the output
  treefj->Write("",TObject::kOverwrite);
  delete ff;

  return 0;
}
