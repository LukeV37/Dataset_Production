#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC2.h"

int main(int argc, char *argv[])
{
    if (argc < 2){
        std::cout << "Error! Must enter 2 arguments" << std::endl;
        std::cout << "1: Dataset Tag (from MadGraph)" << std::endl;
        std::cout << "2: Number of Runs (from MadGraph)" << std::endl;
        return 1;
    }
    char *dataset_tag = argv[1];
    char *run_num = argv[2];

    std::cout << std::string("../../madgraph/WS_")+std::string(dataset_tag)+std::string("/Events/run_01_")+std::string(run_num)+std::string("/unweighted_events.lhe.gz") << std::endl;
    std::string inputFile = std::string("../../madgraph/WS_")+std::string(dataset_tag)+std::string("/Events/run_01_")+std::string(run_num)+std::string("/unweighted_events.lhe.gz");

    // Initialize Pythia Settings
    Pythia8::Pythia pythia;
    pythia.readString("Beams:frameType = 4");
    pythia.readString("Beams:LHEF = "+inputFile);
    Pythia8::Pythia8ToHepMC toHepMC("../shower.hepmc");
    pythia.readString("Next:numberCount = 100");

    // If Pythia fails to initialize, exit with error.
    if (!pythia.init()) return 1;

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

        // Write out event to a hepmc file
        toHepMC.writeNextEvent( pythia );

    } // End pythia event loop

    return 0;
}
