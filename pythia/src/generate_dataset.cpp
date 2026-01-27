#include <iostream>
#include <vector>

#include "TFile.h"
#include "TTree.h"
#include "TRandom3.h"
#include "TString.h"
#include <TRandom.h>

#include "Pythia8/Pythia.h"

#include "fastjet/PseudoJet.hh"
#include "fastjet/ClusterSequence.hh"

#include "include/estimate_ip.h"
#include "include/traverse_history.h"

// Main pythia loop
int main(int argc, char *argv[])
{
    // Using a while loop to iterate through arguments
    char *settings[] = { " ", "In Dataset Tag: ", "Out Dataset Tag: ", "Run Number: ", "Average Pileup (mu): ", "Min pT of Jet: " };
    int i = 0;
    while (i < argc) {
        std::cout << settings[i] << argv[i]
             << std::endl;
        i++;

    }
    if (argc < 5){
        std::cout << "Error! Must enter 5 arguments" << std::endl;
        std::cout << "1: Input Dataset Tag (from MadGraph)" << std::endl;
        std::cout << "2: Output Dataset Tag" << std::endl;
        std::cout << "3: Run Number" << std::endl;
        std::cout << "4: Amount of Pileup, mu" << std::endl;
        std::cout << "5: Min Jet pT (GeV)" << std::endl;
        return 1;
    }

    char *in_dataset_tag = argv[1];
    char *out_dataset_tag = argv[2];
    char *run_num = argv[3];
    int mu = atoi(argv[4]);
    double pTmin_jet = atof(argv[5]);
    
    std::string inputFile = std::string("../../madgraph/WS_")+std::string(in_dataset_tag)+std::string("/Events/run_01_")+std::string(run_num)+std::string("/unweighted_events.lhe.gz");
    TString outputFile = TString("../WS_")+TString(out_dataset_tag)+TString("/data/dataset_showered_run_")+TString(run_num)+TString(".root");

    // Initialiaze output ROOT file
    TFile *output = new TFile(outputFile, "recreate");
    
    // Define local vars to be linked to TTree branches
    int id, ID, label;
    double pT, eta, phi, q, xProd, yProd, zProd, tProd, xDec, yDec, zDec, tDec;

    // Define tree with jets clustered using fast jet
    TTree *FastJet = new TTree("fastjet", "fastjet");
    std::vector<float> jet_pt, jet_eta, jet_phi, jet_m;
    FastJet->Branch("jet_pt", &jet_pt);
    FastJet->Branch("jet_eta", &jet_eta);
    FastJet->Branch("jet_phi", &jet_phi);
    FastJet->Branch("jet_m", &jet_m);

    std::vector<std::vector<int>> jet_trk_association;
    FastJet->Branch("jet_trk_association", &jet_trk_association);

    std::vector<float> trk_pT, trk_eta, trk_phi, trk_q, trk_d0, trk_z0;
    std::vector<int> trk_pid, trk_label, trk_ID, trk_fromBottom, trk_fromW, trk_fromUp, trk_fromDown;
    FastJet->Branch("trk_pT", &trk_pT);
    FastJet->Branch("trk_eta", &trk_eta);
    FastJet->Branch("trk_phi", &trk_phi);
    FastJet->Branch("trk_q", &trk_q);
    FastJet->Branch("trk_d0", &trk_d0);
    FastJet->Branch("trk_z0", &trk_z0);
    FastJet->Branch("trk_pid", &trk_pid);
    FastJet->Branch("trk_label", &trk_label);
    FastJet->Branch("trk_ID", &trk_ID);
    FastJet->Branch("trk_fromBottom", &trk_fromBottom);
    FastJet->Branch("trk_fromW", &trk_fromW);

    // Configure HS Process
    Pythia8::Pythia pythia;

    // Initialize Les Houches Event File run. List initialization information.
    pythia.readString("Beams:frameType = 4");
    pythia.readString(std::string("Beams:LHEF = ")+inputFile);

    pythia.readString("Next:numberCount = 100");

    // Force H->bb decay
    pythia.readString("25:onMode = off");
    pythia.readString("25:onIfAny = 5");

    // Set Vertex Spreading
    pythia.readString("Beams:allowVertexSpread = on");
    pythia.readString("Beams:sigmaVertexX = 0.3");
    pythia.readString("Beams:sigmaVertexY = 0.3");
    pythia.readString("Beams:sigmaVertexZ = 50.");

    // If Pythia fails to initialize, exit with error.
    if (!pythia.init()) return 1;

    // Configure PU Process
    Pythia8::Pythia pythiaPU;
    pythiaPU.readFile("./config/pileup.cmnd");

    // Set Vertex Spreading
    pythiaPU.readString("Beams:allowVertexSpread = on");
    pythiaPU.readString("Beams:sigmaVertexX = 0.3");
    pythiaPU.readString("Beams:sigmaVertexY = 0.3");
    pythiaPU.readString("Beams:sigmaVertexZ = 50.");

    if (mu > 0) pythiaPU.init();

    // Configure antikt_algorithm
    std::map<TString, fastjet::JetDefinition> jetDefs;
    jetDefs["Anti-#it{k_{t}} jets, #it{R} = 0.4"] = fastjet::JetDefinition(fastjet::antikt_algorithm, 0.4, fastjet::E_scheme, fastjet::Best);

    // Allow for possibility of a few faulty events.
    int nAbort = 10;
    int iAbort = 0;

    // Begin Event Loop; generate until none left in input file
    while (iAbort < nAbort) {

        // Generate events, and check whether generation failed.
        if (!pythia.next()) {
          // If failure because reached end of file then exit event loop.
          if (pythia.info.atEndOfFile()) break;
          ++iAbort;
          continue;
        }

        // Track ID starts at zero for each event
        ID = 0;

        // clear previous events
        jet_pt.clear();
        jet_eta.clear();
        jet_phi.clear();
        jet_m.clear();

        trk_pT.clear();
        trk_eta.clear();
        trk_phi.clear();
        trk_q.clear();
        trk_d0.clear();
        trk_z0.clear();
        trk_pid.clear();
        trk_label.clear();
        trk_ID.clear();
        trk_fromBottom.clear();
        trk_fromW.clear();
        trk_fromUp.clear();
        trk_fromDown.clear();

        jet_trk_association.clear();

        // Use depth-first-search to find daughters
        std::vector<int> fromDown;
        std::vector<int> fromUp;
        std::vector<int> fromBottom;
        int top_idx = find_top_from_event(pythia.event, 6);
        int down_idx = find_down_from_top(pythia.event, top_idx);
        int up_idx = find_up_from_top(pythia.event, top_idx);
        int bottom_idx = find_b_from_top(pythia.event, top_idx);
        fromDown = find_daughters(pythia.event, down_idx);
        fromUp = find_daughters(pythia.event, up_idx);
        fromBottom = find_daughters(pythia.event, bottom_idx);

        int entries = pythia.event.size();
        std::vector<fastjet::PseudoJet> stbl_ptcls;

        // Add in hard scatter particles!
        auto &event = pythia.event;
        for(int j=0;j<pythia.event.size();j++){
            auto &p = pythia.event[j];

            if (not p.isFinal()) continue;

            // A.X.: skip neutrinos
            if (abs(p.id())==12 || abs(p.id())==14 || abs(p.id())==16) continue;
            
            // Grab features
            id = p.id();
            pT = p.pT();
            eta = p.eta();
            phi = p.phi();
            q = p.charge();
            xProd = p.xProd();
            yProd = p.yProd();
            zProd = p.zProd();
            tProd = p.tProd();
            xDec = p.xDec();
            yDec = p.yDec();
            zDec = p.zDec();
            tDec = p.tDec();
            double d0,z0; find_ip(pT,eta,phi,xProd,yProd,zProd,d0,z0);

            // Grab label
            label = -1; // HS Process

            // Append features and labels to vector
            trk_pT.push_back(pT);
            trk_eta.push_back(eta);
            trk_phi.push_back(phi);
            trk_q.push_back(q);
            trk_d0.push_back(d0);
            trk_z0.push_back(z0);
            trk_pid.push_back(id);
            trk_label.push_back(label);
            trk_ID.push_back(ID);
            trk_fromBottom.push_back(fromBottom[j]);
            int fromW=0;
            if ((fromUp[j]==1)||(fromDown[j]==1)){fromW=1;}
            trk_fromW.push_back(fromW);

            // Store particles for jet clustering
            fastjet::PseudoJet fj(p.px(), p.py(), p.pz(), p.e());
            fj.set_user_index(ID++);
            stbl_ptcls.push_back(fj);
        }

        // Add in pileup particles!
        int n_inel = 0;
        if (mu>0) {
            n_inel = gRandom->Poisson(mu);
            // printf("Overlaying particles from %i pileup interactions!\n", n_inel);
        }
        for (int i_pu= 0; i_pu<n_inel; ++i_pu) {
            if (!pythiaPU.next()) continue;
            for (int j = 0; j < pythiaPU.event.size(); ++j) {
                auto &p = pythiaPU.event[j];

                if (not p.isFinal()) continue;

                // A.X.: skip neutrinos
                if (abs(p.id())==12 || abs(p.id())==14 || abs(p.id())==16) continue;
                
                // Grab features
                id = p.id();
                pT = p.pT();
                eta = p.eta();
                phi = p.phi();
                q = p.charge();
                xProd = p.xProd();
                yProd = p.yProd();
                zProd = p.zProd();
                tProd = p.tProd();
                xDec = p.xDec();
                yDec = p.yDec();
                zDec = p.zDec();
                tDec = p.tDec();
                double d0,z0; find_ip(pT,eta,phi,xProd,yProd,zProd,d0,z0);

                // Grab label
                label = i_pu; // PU Process

                // Append features and labels to vector
                trk_pT.push_back(pT);
                trk_eta.push_back(eta);
                trk_phi.push_back(phi);
                trk_q.push_back(q);
                trk_d0.push_back(d0);
                trk_z0.push_back(z0);
                trk_pid.push_back(id);
                trk_label.push_back(label);
                trk_ID.push_back(ID);
                trk_fromBottom.push_back(0);
                trk_fromW.push_back(0);

                // Store particles for jet clustering
                fastjet::PseudoJet fj(p.px(), p.py(), p.pz(), p.e());
                fj.set_user_index(ID++);
                stbl_ptcls.push_back(fj);
            }
        }

        // Cluster stable particles using anti-kt
        for (auto jetDef:jetDefs) {
            fastjet::ClusterSequence clustSeq(stbl_ptcls, jetDef.second);
            auto jets = fastjet::sorted_by_pt( clustSeq.inclusive_jets(pTmin_jet) );
            // For each jet:
            for (auto jet:jets) {
                jet_pt.push_back(jet.pt());
                jet_eta.push_back(jet.eta());
                jet_phi.push_back(jet.phi());
                jet_m.push_back(jet.m());

                std::vector<int> jet_trk_association_tmp;

                // For each particle:
                for (auto trk:jet.constituents()) {
                    jet_trk_association_tmp.push_back(trk.user_index());
                }
                
                jet_trk_association.push_back(jet_trk_association_tmp);
            }
        }
        FastJet->Fill();
    }

    output->Write();
    output->Close();

    return 0;
}
