SUBMODULES_PATH=../../../submodules/

CPP=g++
LD=g++
SPECIALFLAGS=-O2
ROOTCFLAGS=$(shell root-config --cflags)
ROOTLIBS=$(shell root-config --libs)

CFLAGS = $(SPECIALFLAGS) -I.
LFLAGS = -L.

RCXX=$(CFLAGS) $(ROOTCFLAGS)
RLXX=$(LFLAGS) $(ROOTLIBS)

SRC1=add_JVT.cpp add_JVT_dict.cpp
SRC2=add_true_EMfrac.cpp add_true_EMfrac_dict.cpp

add_JVT_dict.cpp: ../include/LinkDef.h
	@rootcling add_JVT_dict.cpp ../include/LinkDef.h

add_true_EMfrac_dict.cpp: ../include/LinkDef.h
	@rootcling add_true_EMfrac_dict.cpp ../include/LinkDef.h

%.o: %.cpp
	@$(CPP) $(RCXX) -c $< -w -O2 -std=c++17

add_JVT: $(SRC1:.cpp=.o)
	@$(LD) $(SRC1:.cpp=.o) $(RLXX) -o add_JVT -w -O2 -std=c++17 $(shell root-config --libs --cflags)

add_true_EMfrac: $(SRC2:.cpp=.o)
	@$(LD) $(SRC2:.cpp=.o) $(RLXX) -o add_true_EMfrac -w 

clean:
	@rm -f add_JVT add_true_EMfrac 
	@rm -f add_*_dict* *.o
	@rm -f file 
