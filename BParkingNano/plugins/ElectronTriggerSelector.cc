// A class to produce two pat::ElectronCollections
// - one matched to the di-electron triggers
// - another filtered w.r.t. the di-electron triggers


#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Utilities/interface/StreamID.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "DataFormats/PatCandidates/interface/Electron.h"

#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"
#include "DataFormats/PatCandidates/interface/TriggerPath.h"
#include "DataFormats/PatCandidates/interface/TriggerEvent.h"
#include "DataFormats/PatCandidates/interface/TriggerAlgorithm.h"

#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"

#include <TLorentzVector.h>
#include "helper.h"

using namespace std;

constexpr int debug = 0;

class ElectronTriggerSelector : public edm::stream::EDProducer<> {
    
public:
    
    explicit ElectronTriggerSelector(const edm::ParameterSet &iConfig);
    
    ~ElectronTriggerSelector() override {};
    
    
private:

    virtual void produce(edm::Event&, const edm::EventSetup&);
    void print(edm::Event&,
	       edm::Handle<edm::TriggerResults>&,
	       edm::Handle<std::vector<pat::TriggerObjectStandAlone>>&);

    const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;
    edm::EDGetTokenT<std::vector<pat::Electron>> electronSrc_;
    edm::EDGetTokenT<edm::TriggerResults> triggerBits_;
    edm::EDGetTokenT<std::vector<pat::TriggerObjectStandAlone>> triggerObjects_;
    edm::EDGetTokenT<pat::PackedTriggerPrescales> triggerPrescales_;
    edm::EDGetTokenT<reco::VertexCollection> vertexSrc_;
    //for trigger match
    const double maxdR_;

    //for filter wrt trigger
    const double dzTrg_cleaning_; // selects primary vertex
    const bool filterElectron_;

    const double ptMin_;          // min pT in all electrons for B candidates
    const double absEtaMax_;      //max eta ""
    std::vector<std::string> HLTPaths_;
    std::vector<std::string> L1Seeds_;
};


ElectronTriggerSelector::ElectronTriggerSelector(const edm::ParameterSet &iConfig):
  bFieldToken_(esConsumes<MagneticField, IdealMagneticFieldRecord>()),
  electronSrc_( consumes<std::vector<pat::Electron>> ( iConfig.getParameter<edm::InputTag>( "electronCollection" ) ) ),
  triggerBits_(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("bits"))),
  triggerObjects_(consumes<std::vector<pat::TriggerObjectStandAlone>>(iConfig.getParameter<edm::InputTag>("objects"))),
  triggerPrescales_(consumes<pat::PackedTriggerPrescales>(iConfig.getParameter<edm::InputTag>("prescales"))),
  vertexSrc_( consumes<reco::VertexCollection> ( iConfig.getParameter<edm::InputTag>( "vertexCollection" ) ) ), 
  maxdR_(iConfig.getParameter<double>("maxdR_matching")),
  dzTrg_cleaning_(iConfig.getParameter<double>("dzForCleaning_wrtTrgElectron")),
  filterElectron_(iConfig.getParameter<bool>("filterElectron")),
  ptMin_(iConfig.getParameter<double>("ptMin")),
  absEtaMax_(iConfig.getParameter<double>("absEtaMax")), 
  HLTPaths_(iConfig.getParameter<std::vector<std::string>>("HLTPaths")),
  L1Seeds_(iConfig.getParameter<std::vector<std::string>>("L1seeds"))
{
  // produce 2 collections: trgElectrons (tags) and SelectedElectrons (probes & tags if survive preselection cuts)
    produces<pat::ElectronCollection>("trgElectrons"); 
    produces<pat::ElectronCollection>("SelectedElectrons");
    produces<TransientTrackCollection>("SelectedTransientElectrons");  
}


// Based on: https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2017#Trigger
// 
void ElectronTriggerSelector::print(edm::Event& iEvent,
				    edm::Handle<edm::TriggerResults>& triggerBits,
				    edm::Handle<std::vector<pat::TriggerObjectStandAlone>>& triggerObjects) {

  std::vector<std::string> present;
  bool fired = false;
  const edm::TriggerNames &names = iEvent.triggerNames(*triggerBits);
  std::cout << "\n == TRIGGER PATHS= " << std::endl;
  for (unsigned int i = 0, n = triggerBits->size(); i < n; ++i) {
    std::string name = names.triggerName(i);
    name = name.substr(0,name.find("_v"));
    if ( std::find(HLTPaths_.begin(), HLTPaths_.end(), name) == HLTPaths_.end() ) { continue; }
    present.push_back(name);
    std::cout << "Trigger " << names.triggerName(i) <<
      //", prescale " << triggerPrescales->getPrescaleForIndex(i) <<
      ": " << (triggerBits->accept(i) ? "PASS" : "fail (or not run)")
	      << std::endl;
    if ( triggerBits->accept(i) ) fired = true;
  }

  if ( !present.empty() ) {
    std::cout << "  Trigger present";
    if ( fired ) std::cout << " and fired! ";
    std::cout << std::endl;
    for ( const auto& name : present ) { std::cout << "    " << name << std::endl; }
  } else {
    std::cout << "TRIGGER MISSING!" << std::endl;
  }
//  return;//@@

  std::cout << "\n TRIGGER OBJECTS " << std::endl;
  //for (pat::TriggerObjectStandAlone obj : *triggerObjects) { // note: not "const &" since we want to call unpackPathNames
  for (unsigned int i = 0, n = triggerObjects->size(); i < n; ++i) {
    pat::TriggerObjectStandAlone obj = (*triggerObjects)[i];
    //std::string name = names.triggerName(i);
    //name = name.substr(0,name.find("_v"));
    //if ( std::find(HLTPaths_.begin(), HLTPaths_.end(), name) == HLTPaths_.end() ) { continue; }
    //obj.unpackPathNames(names);
    obj.unpackNamesAndLabels(iEvent,*triggerBits);
    std::cout << "\tTrigger object:  pt " << obj.pt() << ", eta " << obj.eta() << ", phi " << obj.phi() << std::endl;
    // Print trigger object collection and type
    std::cout << "\t   Collection: " << obj.collection() << std::endl;
    std::cout << "\t   Type IDs:   ";
    for (unsigned h = 0; h < obj.filterIds().size(); ++h) std::cout << " " << obj.filterIds()[h] ;
    std::cout << std::endl;
    // Print associated trigger filters
    std::cout << "\t   Filters:    ";
    for (unsigned h = 0; h < obj.filterLabels().size(); ++h) std::cout << " " << obj.filterLabels()[h];
    std::cout << std::endl;
    std::vector pathNamesAll = obj.pathNames(false);
    std::vector pathNamesLast = obj.pathNames(true);
    // Print all trigger paths, for each one record also if the object is associated to a 'l3' filter (always true for the
    // definition used in the PAT trigger producer) and if it's associated to the last filter of a successfull path (which
    // means that this object did cause this trigger to succeed; however, it doesn't work on some multi-object triggers)
    std::cout << "\t   Paths (" << pathNamesAll.size()<<"/"<<pathNamesLast.size()<<"):    ";
    for (unsigned h = 0, n = pathNamesAll.size(); h < n; ++h) {
      bool isBoth = obj.hasPathName( pathNamesAll[h], true, true );
      bool isL3   = obj.hasPathName( pathNamesAll[h], false, true );
      bool isLF   = obj.hasPathName( pathNamesAll[h], true, false );
      bool isNone = obj.hasPathName( pathNamesAll[h], false, false );
      std::cout << "   " << pathNamesAll[h];
      if (isBoth) std::cout << "(L,3)";
      if (isL3 && !isBoth) std::cout << "(*,3)";
      if (isLF && !isBoth) std::cout << "(L,*)";
      if (isNone && !isBoth && !isL3 && !isLF) std::cout << "(*,*)";
    }
    std::cout << std::endl;
  }
  std::cout << std::endl;

}

void ElectronTriggerSelector::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
    if(debug>0)
      std::cout	<< "[ElectronTriggerSelector::produce]"
		<< std::endl;
    
    const auto& bField = iSetup.getData(bFieldToken_);
    edm::Handle<reco::VertexCollection> vertexHandle;
    iEvent.getByToken(vertexSrc_, vertexHandle);
//    const reco::Vertex & PV = vertexHandle->front();

    edm::Handle<edm::TriggerResults> triggerBits;
    iEvent.getByToken(triggerBits_, triggerBits);
//    const edm::TriggerNames &names = iEvent.triggerNames(*triggerBits);

    std::vector<pat::TriggerObjectStandAlone> triggeringElectrons;

    //taken from https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2016#Trigger
    edm::Handle<std::vector<pat::TriggerObjectStandAlone>> triggerObjects;
    iEvent.getByToken(triggerObjects_, triggerObjects);

    if(debug>1) print(iEvent,triggerBits,triggerObjects);

    std::unique_ptr<pat::ElectronCollection> trgelectrons_out( new pat::ElectronCollection );
    std::unique_ptr<pat::ElectronCollection> electrons_out( new pat::ElectronCollection );
    std::unique_ptr<TransientTrackCollection> trans_electrons_out( new TransientTrackCollection );

    //now check for reco electrons matched to triggering electrons
    edm::Handle<std::vector<pat::Electron>> electrons;
    iEvent.getByToken(electronSrc_, electrons);

    std::vector<int> electronIsTrigger(electrons->size(), 0);
    std::vector<float> electronDR(electrons->size(),-1.);
    std::vector<float> electronDPT(electrons->size(),10000.);
    std::vector<int> loose_id(electrons->size(),0);

    std::vector<int> matched_reco_flag(electrons->size(),-1);
    std::vector<int> matched_trg_index(electrons->size(),-1);
    std::vector<float> matched_dr(electrons->size(),-1.);
    std::vector<float> matched_dpt(electrons->size(),-10000.);
    std::vector<std::vector<int>> fires;
    std::vector<std::vector<float>> matcher; 
    std::vector<std::vector<float>> DR;
    std::vector<std::vector<float>> DPT;    

    int nele = 0;
    int mele = 0;
    for(const pat::Electron & electron : *electrons){
      //unsigned int iEle(&electron - &(electrons->at(0)) );
        if(electron.pt()<ptMin_) continue;
        if(fabs(electron.eta())>absEtaMax_) continue;
	if(debug>1)
	  std::cout << "nele=" << nele
		    << " pt=" << electron.pt()
		    << " eta=" << electron.eta()
		    << " phi=" << electron.phi()
		    << std::endl;
	nele++;
	if(electron.triggerObjectMatches().empty()) continue;
	mele++;
    }

    if(debug>1)
      std::cout	<< " nele (inAcc)=" << nele
		<< " mele (isMatched)=" << mele
		<< std::endl;
    if(debug>0)
      std::cout	<< " Number of L1 seeds=" << L1Seeds_.size()
		<< " Number of HLT paths=" << HLTPaths_.size()
		<< " Number of triggerObjects=" << triggerObjects->size()
		<< " Number of electrons=" << electrons->size()
		<< std::endl;

    for(const pat::Electron &electron : *electrons){
        if(debug>1)
	  std::cout << "Electron Pt=" << electron.pt() 
		    << " Eta=" << electron.eta() 
		    << " Phi=" << electron.phi()
		    << " NtriggerObjectMatches=" << electron.triggerObjectMatches().size()
		    << std::endl;
        std::vector<int> frs(HLTPaths_.size(),0); //path fires for each reco electron
        std::vector<int> sds(L1Seeds_.size(),0);// L1 Seeds for each L1 electron
        std::vector<float> temp_matched_to(HLTPaths_.size(),1000.);
        std::vector<float> temp_DR(HLTPaths_.size(),1000.);
        std::vector<float> temp_DPT(HLTPaths_.size(),1000.);
        int ipath=-1;
        int iseed=-1;

        for (const std::string& seed: L1Seeds_){
	  iseed++;
	  char cstr[(seed+"*").size()+1];
	  strcpy( cstr,(seed+"*").c_str());
	  if(electron.triggerObjectMatches().size()!=0){
	    for(size_t i=0;i<electron.triggerObjectMatches().size(); i++){
	      if(debug>1) {
          std::cout << "  iMatch=" << i << " PathNames=";
          for(auto const & name : electron.triggerObjectMatch(i)->pathNames()){
            std::cout << " " << name;
          }
          std::cout << " AlgoNames=";
          for(auto const & name : electron.triggerObjectMatch(i)->algorithmNames()){
            std::cout << " " << name;
          }
          std::cout << std::endl;
	      }
	      if(electron.triggerObjectMatch(i)!=0 && electron.triggerObjectMatch(i)->hasAlgorithmName(cstr,true)){
		sds[iseed]=1;
		if(debug>1)
		  std::cout << "  L1 Seed=" << cstr
			    << " fired=" << sds[iseed]
			    << std::endl;
	      }
	    }
	  }
        }

        for (const std::string& path: HLTPaths_){
            ipath++;
            // the following vectors are used in order to find the minimum DR between a reco electron and all the HLT objects that is matched with it so as a reco electron will be matched with only one HLT object every time so as there is a one-to-one correspondance between the two collection. DPt_rel is not used to create this one-to-one correspondance but only to create a few plots, debugging and be sure thateverything is working fine.
	    // RB: deltaR match determined for trigger (eta,phi) and electron SuperCluster (eta,phi) positions ...
            std::vector<float> temp_dr(electron.triggerObjectMatches().size(),1000.);
            std::vector<float> temp_dpt(electron.triggerObjectMatches().size(),1000.);
            std::vector<float> temp_pt(electron.triggerObjectMatches().size(),1000.);
            char cstr[ (path+"*").size() + 1];
	    strcpy( cstr, (path+"*").c_str() );       
	    if(debug>1) 
	      std::cout << "  HLT path=" << cstr << endl;
            //Here we find all the HLT objects from each HLT path each time that are matched with the reco electron.
            if(electron.triggerObjectMatches().size()!=0){
                for(size_t i=0; i<electron.triggerObjectMatches().size();i++){
//                if(electron.triggerObjectMatch(i)!=0 && electron.triggerObjectMatch(i)->hasAlgorithm)
		  if(debug>1) {
		    if (electron.triggerObjectMatch(i)!=0) {
		      std::cout << "  iMatch=" << i << " PathNames=";
		      for(auto const & name : electron.triggerObjectMatch(i)->pathNames()){
			std::cout << " " << name;
		      }
		      std::cout << " AlgoNames=";
		      for(auto const & name : electron.triggerObjectMatch(i)->algorithmNames()){
			std::cout << " " << name;
		      }
		      std::cout << std::endl;
		    }
		  }
		  if(debug>1) {
		    if(electron.triggerObjectMatch(i)!=0 ) {
		      std::cout << "HERE0 "
				<< cstr << " "
				<< electron.triggerObjectMatch(i)->hasPathName(cstr,false,false) << " "
				<< electron.triggerObjectMatch(i)->hasPathName(cstr,false,true) << " "
				<< electron.triggerObjectMatch(i)->hasPathName(cstr,true,false) << " "
				<< electron.triggerObjectMatch(i)->hasPathName(cstr,true,true) << " "
				<< electron.triggerObjectMatch(i)->hasPathLastFilterAccepted() << " "
				<< electron.triggerObjectMatch(i)->hasPathL3FilterAccepted() << " "
				<< std::endl;
		    }
		  }
		    if(electron.triggerObjectMatch(i)!=0 && electron.triggerObjectMatch(i)->hasPathName(cstr,false,true)){
		      //if(abs(electron.triggerObjectMatch(i)->eta())>1.5) std::cout << "HEEEEEEEEEEEEEEEEEEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE eta=" <<electron.triggerObjectMatch(i)->eta();
		        if(debug>1) std::cout << "HERE1" << std::endl;
                        frs[ipath]=1;
			// RB: deltaR match determined for trigger (eta,phi) and electron SuperCluster (eta,phi) positions ...
                        float dr=TMath::Sqrt(pow(electron.triggerObjectMatch(i)->eta()-electron.superCluster()->eta(),2.)+
					     pow(electron.triggerObjectMatch(i)->phi()-electron.superCluster()->phi(),2.));
                        float dpt=(electron.triggerObjectMatch(i)->pt()-electron.pt())/electron.triggerObjectMatch(i)->pt();
                        temp_dr[i]=dr;
                        temp_dpt[i]=dpt;
                        temp_pt[i]=electron.triggerObjectMatch(i)->pt();                   
                        //if(debug>1)std::cout <<" Path=" <<cstr << endl;
                        if(debug>1)std::cout <<" HLT  Pt="<<electron.triggerObjectMatch(i)->pt() <<" Eta="<<electron.triggerObjectMatch(i)->eta() <<" Phi="<<electron.triggerObjectMatch(i)->phi() << endl;
                        if(debug>1)std::cout <<" Electron Pt="<< electron.pt() << " Eta=" << electron.eta() << " Phi=" << electron.phi()  <<endl;
                        if(debug>1)std::cout <<" DR = " << temp_dr[i] <<endl;
                    }
                }
                // and now we find the real minimum between the reco electron and all its matched HLT objects. 
                temp_DR[ipath]=*min_element(temp_dr.begin(),temp_dr.end());
                int position=std::min_element(temp_dr.begin(),temp_dr.end()) - temp_dr.begin();
                temp_DPT[ipath]=temp_dpt[position];
                temp_matched_to[ipath]=temp_pt[position];
                }
            }
        //and now since we have found the minimum DR we save a few variables for plots       
        fires.push_back(frs);//This is used in order to see if a reco electron fired a Trigger (1) or not (0).
        matcher.push_back(temp_matched_to); //This is used in order to see if a reco electron is matched with a HLT object. PT of the reco electron is saved in this vector. 
        DR.push_back(temp_DR);
        DPT.push_back(temp_DPT);

    }

    //now, check for different reco electrons that are matched to the same HLTObject.
    for(unsigned int path=0; path<HLTPaths_.size(); path++){
        for(unsigned int iEle=0; iEle<electrons->size(); iEle++){
            for(unsigned int ie=(iEle+1); ie<electrons->size(); ie++){
                if(matcher[iEle][path]!=1000. && matcher[iEle][path]==matcher[ie][path]){
                    if(DR[iEle][path]<DR[ie][path]){ //Keep the one that has the minimum DR with the HLT object
                        fires[ie][path]=0;
                        matcher[ie][path]=1000.;
                        DR[ie][path]=1000.;                       
                        DPT[ie][path]=1000.;
                    }
                    else{
                        fires[iEle][path]=0;
                        matcher[iEle][path]=1000.;
                        DR[iEle][path]=1000.;                       
                        DPT[iEle][path]=1000.;
                    }
                }              
            }
            if(matcher[iEle][path]!=1000.){
                electronIsTrigger[iEle]=1;
                electronDR[iEle]=DR[iEle][path];
                electronDPT[iEle]=DPT[iEle][path];                
            }
        }
    }
    if(debug>1)std::cout << "number of Electrons=" <<electrons->size() << endl;

    //And now create a collection with all trg electrons
    for(const pat::Electron & electron : *electrons){
        unsigned int iEle(&electron -&(electrons->at(0)));
        if(electronIsTrigger[iEle]==1){
            pat::Electron recoTriggerElectronCand(electron);
            trgelectrons_out->emplace_back(recoTriggerElectronCand);
        }
    }

    //and now save the reco electron triggering or not 
    for(const pat::Electron & electron : *electrons){
        unsigned int iEle(&electron - &(electrons->at(0)) );
        if(electron.pt()<ptMin_) continue;
        if(fabs(electron.eta())>absEtaMax_) continue;
        //if(electron.isLooseElectron()){loose_id[iEle] = 1;}

        bool SkipElectron=true;
        if(dzTrg_cleaning_<0) SkipElectron=false;
        if(debug>1 && trgelectrons_out->size()==0) std::cout <<"HERE!! trgelectrons_out->size()==0" << endl;
        for(const pat::Electron & trgele : *trgelectrons_out){
            if(fabs(electron.vz()-trgele.vz())> dzTrg_cleaning_ && dzTrg_cleaning_>0) continue;
            SkipElectron=false;
        }
        if(filterElectron_ && SkipElectron) continue;

        const reco::TransientTrack electronTT((*(electron.bestTrack())),&bField); // need this?
        if(!electronTT.isValid()) continue; // need this?

        electrons_out->emplace_back(electron);
        electrons_out->back().addUserInt("isTriggering", electronIsTrigger[iEle]);
        electrons_out->back().addUserFloat("DR",electronDR[iEle]);
        electrons_out->back().addUserFloat("DPT",electronDPT[iEle]);
        electrons_out->back().addUserInt("looseId",loose_id[iEle]);
        electrons_out->back().addUserInt("skipElectron",SkipElectron);

        for(unsigned int i=0; i<HLTPaths_.size(); i++){electrons_out->back().addUserInt(HLTPaths_[i],fires[iEle][i]);}
        trans_electrons_out->emplace_back(electronTT);


    }
 
    if(debug>0) {
      std::cout << "Number of trgElectrons=" <<trgelectrons_out->size() << endl;
      std::cout << "Number of SelectedElectrons=" <<electrons_out->size() << endl;
      std::cout << "Number of SelectedTransientElectrons=" <<trans_electrons_out->size() << endl;
    }

    iEvent.put(std::move(trgelectrons_out),    "trgElectrons"); 
    iEvent.put(std::move(electrons_out),       "SelectedElectrons");
    iEvent.put(std::move(trans_electrons_out), "SelectedTransientElectrons");
}



DEFINE_FWK_MODULE(ElectronTriggerSelector);
