#include <TTree.h>
#include <TFile.h>

#include <vector>
using std::vector;

#include <iostream>
using std::cout;
using std::endl;

#include <cmath>

int main(int argc, char *argv[])
{

  char *name = argv[1];

  // the existing tree will be updated!
  TFile* ff = new TFile(TString(name), "update");

  // fastjet ntuple
  TTree* treefj = (TTree*)ff->Get("fastjet");

  // new branches to add
  vector<float> jet_corrJVF;
  TBranch* jet_corrJVF_branch = treefj->Branch("jet_corrJVF", &jet_corrJVF);
  vector<float> jet_RpT;
  TBranch* jet_RpT_branch = treefj->Branch("jet_RpT", &jet_RpT);

  // existing branches to use

  vector<float>* jet_pT;
  vector<float>* trk_pT;
  vector<float>* trk_q;
  vector<int>* trk_label;
  vector< vector<int> >* jet_trk_association;

  treefj->SetBranchAddress("jet_pt", &jet_pT);
  treefj->SetBranchAddress("trk_pT", &trk_pT);
  treefj->SetBranchAddress("trk_q", &trk_q);
  treefj->SetBranchAddress("trk_label", &trk_label);
  treefj->SetBranchAddress("jet_trk_association", &jet_trk_association);

  // loop over fastjet
  int nevfj = treefj->GetEntries();
  cout << "fastjet entries: " << nevfj << endl;
  for (int ievfj = 0; ievfj<nevfj; ++ievfj) {
    if (ievfj%1000==0) { cout << ievfj << '\r'; cout.flush(); }

    jet_pT = 0;
    trk_pT = 0;
    trk_q = 0;
    trk_label = 0;
    jet_trk_association = 0;
    
    float k = 0.01;
    int num_PU = 0;

    treefj->GetEntry(ievfj);

    // First count number of PU tracks per event
    int ntrk = trk_pT->size();
    for (int itrk = 0; itrk<ntrk; ++itrk){
        // skip neutrals
        if ((*trk_q)[itrk]==0) continue;
        // skip low pT particles
        double pttr = (*trk_pT)[itrk];
        if (pttr<0.4) continue;
        // count num_PU
        int label = (*trk_label)[itrk];
        if (label>=0) num_PU++;
    }

    // loop over jets
    int njet = jet_pT->size();
    jet_corrJVF = vector<float>(njet,-1);
    jet_RpT = vector<float>(njet,-1);
    for (int ijet = 0; ijet<njet; ++ijet) {
        // loop over tracks
        int ntr = (*jet_trk_association)[ijet].size();
        double sumpt_hs = 0, sumpt_pu = 0;
        for (int itr = 0; itr<ntr; ++itr) {
            int trk_idx = (*jet_trk_association)[ijet][itr];
	        // skip neutrals
            if ((*trk_q)[trk_idx]==0) continue;
            // skip low pT particles
            double pttr = (*trk_pT)[trk_idx];
            if (pttr<0.4) continue;
            // collect weights
            int label = (*trk_label)[trk_idx];
            double weight = pow(pttr,1);
            if (label==-1) sumpt_hs += weight;
            if (label>=0) sumpt_pu += weight;
        }
        if ((sumpt_hs+sumpt_pu)>0) jet_corrJVF[ijet] = sumpt_hs/(sumpt_hs+sumpt_pu/(k*num_PU+0.000000001)+0.0000001);
        if ((*jet_pT)[ijet]>0) jet_RpT[ijet] = sumpt_hs/(*jet_pT)[ijet];
    }
    jet_corrJVF_branch->Fill();
    jet_RpT_branch->Fill();
  }

  // save the output
  treefj->Write("",TObject::kOverwrite);
  delete ff;

  return 0;
}
