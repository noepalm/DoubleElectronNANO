// -*- C++ -*-
//
// Package:    PhysicsTools/lowPtIDProducer
// Class:      lowPtIDProducer
//
/**\class lowPtIDProducer lowPtIDProducer.cc PhysicsTools/NanoAOD/plugins/lowPtIDProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Wesley Terrill
//         Created:  Wed, 04 Jun 2025 15:49:05 GMT
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/EgammaCandidates/interface/GsfElectron.h"

#include "CommonTools/BaseParticlePropagator/interface/BaseParticlePropagator.h"
#include "CommonTools/BaseParticlePropagator/interface/RawParticle.h"
#include "CommonTools/MVAUtils/interface/GBRForestTools.h"
#include "CondFormats/GBRForest/interface/GBRTree.h"

#include <iostream>
#include <fstream>

#include "TVector3.h"
#include <Math/VectorUtil.h>


void findEnergeticClusters(
  reco::SuperClusterRef const& sc, int& clusNum, float& maxEne1, float& maxEne2, int& i1, int& i2){
  if(sc->clustersSize()>0 && sc->clustersBegin()!=sc->clustersEnd()){
    for(auto const& cluster : sc->clusters()){
      if(cluster->energy() > maxEne1){
        maxEne1 = cluster->energy();
        i1 = clusNum;
      }
      clusNum++;
    }
    if(sc->clustersSize()>1){
      clusNum=0;
      for(auto const& cluster : sc->clusters()){
        if(clusNum!=i1){
          if(cluster->energy()>maxEne2){
            maxEne2 = cluster->energy();
            i2=clusNum;
          }
        }
        clusNum++;
      }
    }
  }
}

//
// class declaration
//

class lowPtIDProducer : public edm::stream::EDProducer<> {
public:
  explicit lowPtIDProducer(const edm::ParameterSet&);
  ~lowPtIDProducer() override;

  typedef std::vector<pat::Electron> electronCollection;

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  void beginStream(edm::StreamID) override;

  void produce(edm::Event&, const edm::EventSetup&) override;
  void endStream() override;

  const edm::EDGetTokenT<std::vector<pat::Electron> > src_;
  const edm::EDGetTokenT<double> rho_;
  const edm::EDGetTokenT<edm::View<reco::GenParticle>> genParticles_;

  const std::string modelFile_;
  GBRForest* forest_;

  // ----------member data ---------------------------
  const bool isMC_;
  const bool doMatch_;
  const float deltaR_;
  
  float trk_p_;
  float trk_chi2red_;
  float trk_dr_;
  float trk_nhits_;

  float gsf_mode_p_;
  float gsf_chi2red_;
  float gsf_dr_;
  float gsf_nhits_;

  float sc_clus1_nxtal_;
  float sc_clus1_dphi_;
  float sc_clus1_deta_;
  float sc_clus1_E_;
  float sc_clus1_EoverP_;
  float sc_clus2_dphi_;
  float sc_clus2_deta_;
  float sc_clus2_E_;
  float sc_clus2_EoverP_;

  int matchToTruth(reco::GsfElectron const&, edm::View<reco::GenParticle> const&) const;
};

enum ElectronMatchType{
  UNMATCHED,
  TRUE_PROMPT_ELECTRON,
  TRUE_ELECTRON_FROM_TAU,
  TRUE_NON_PROMPT_ELECTRON
};

//
// constructors and destructor
//
lowPtIDProducer::lowPtIDProducer(const edm::ParameterSet& iConfig) 
    : src_(consumes<std::vector<pat::Electron>>(iConfig.getParameter<edm::InputTag>("src"))),
      rho_(consumes<double>(iConfig.getParameter<edm::InputTag>("rho"))),
      genParticles_(consumes<edm::View<reco::GenParticle>>(iConfig.getParameter<edm::InputTag>("genParticles"))),
      modelFile_(iConfig.getParameter<std::string>("modelFile")),
      isMC_(iConfig.getParameter<bool>("isMC")),
      doMatch_(iConfig.getParameter<bool>("doMatch")),
      deltaR_(iConfig.getParameter<double>("deltaR")){
  //Register the ValueMap with the label ID
  produces<edm::ValueMap<float>>("ids");
  if(isMC_ && doMatch_){produces<edm::ValueMap<int>>("matchedToGenEle");}
  edm::FileInPath weightfile(modelFile_);
  std::unique_ptr<TFile> file(TFile::Open(weightfile.fullPath().c_str()));
  if(!file || file->IsZombie()){
    throw cms::Exception("MissingModelFile") << "Could not open file: " << weightfile.fullPath() << std::endl;
  }
  forest_ = (GBRForest*) file->Get("gbrForest");
  if(!forest_){
    auto keys = file->GetListOfKeys();
    if(!keys || keys->IsEmpty()){
      edm::LogError("ModelFile")<<"No objects found in file: "<<weightfile.fullPath();
    }
    else{
      for(TIter it(keys); auto* key = (TKey*)it();){
        edm::LogInfo("ModelFile")<<"Object: "<<key->GetName()<<" of class "<<key->GetClassName();
      }
    }
    throw cms::Exception("MissingForest") << "Could not retrieve GBRForest from file\n";
  }
}

lowPtIDProducer::~lowPtIDProducer() {
}

//
// member functions
//

// ------------ method called to produce the data  ------------
void lowPtIDProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup) {
  const auto& rho = iEvent.get(rho_);

  edm::Handle<std::vector<pat::Electron>> electrons;
  iEvent.getByToken(src_, electrons);
  
  auto genParticles = iEvent.getHandle(genParticles_);

  std::vector<float> ids;
  std::vector<int>   matchedToGenEle;

  //This is where the necessary features are filled to extract the raw ID values later
  for(auto const& ele : *electrons){
    std::vector<float> features;

    // superCluster Features
    features.push_back(ele.superCluster()->eta());
    features.push_back(ele.superCluster()->etaWidth());
    features.push_back(ele.superCluster()->phiWidth());
    features.push_back(ele.superCluster()->energy());
    features.push_back(ele.superCluster()->clustersSize());
    
    // electron features
    features.push_back(ele.full5x5_r9());
    features.push_back(ele.full5x5_hcalOverEcal());
    features.push_back(ele.full5x5_sigmaIetaIeta());
    features.push_back(ele.full5x5_sigmaIphiIphi());
    features.push_back(1. - ele.full5x5_e1x5() / ele.full5x5_e5x5());
    features.push_back(ele.fbrem());
    features.push_back(ele.eSuperClusterOverP());
    features.push_back(fabs(ele.deltaEtaSuperClusterTrackAtVtx()));
    features.push_back(fabs(ele.deltaPhiSuperClusterTrackAtVtx()));
    features.push_back(fabs(ele.deltaEtaSeedClusterTrackAtCalo()));
    features.push_back(ele.shFracInnerHits());
    features.push_back(((1. / ele.ecalEnergy()) - (1. / ele.p())));
    features.push_back(ele.electronID("unbiased"));

    // generic features
    features.push_back(rho);

    //trk features
    reco::TrackRef trackRef = ele.closestCtfTrackRef();
    if(trackRef.isNonnull() && trackRef.isAvailable() && ele.core().isNonnull()){
        trk_p_ = trackRef->p();
        trk_chi2red_ = trackRef->normalizedChi2();
        trk_dr_ = reco::deltaR(*trackRef, ele);
        trk_nhits_ = trackRef->found();
    }
    else{
        trk_p_ = -999.;
        trk_chi2red_ = -999.;
        trk_dr_ = -999;
        trk_nhits_ = -999.;
    }
    features.push_back(trk_p_);
    features.push_back(trk_chi2red_);
    features.push_back(trk_dr_);
    features.push_back(trk_nhits_);

    //gsf features
    if(ele.core().isNonnull()){
        reco::GsfTrackRef gsf = ele.gsfTrack();
        if(gsf.isNonnull()){
            gsf_mode_p_ = gsf->pMode();
            gsf_chi2red_ = gsf->normalizedChi2();
            gsf_nhits_ = (float)gsf->found();

            TVector3 gsfTV3(0,0,0);
            TVector3 eleTV3(0,0,0);
            gsfTV3.SetPtEtaPhi(gsf->ptMode(), gsf->etaMode(), gsf->phiMode());
            eleTV3.SetPtEtaPhi(ele.pt(), ele.eta(), ele.phi());
            gsf_dr_ = eleTV3.DeltaR(gsfTV3);
        
            //track cluster matching (sc_clus1 and sc_clus2)
            reco::SuperClusterRef sc = ele.superCluster();
            if(sc.isNonnull()){
                //propagate electron track to ECAL surface
                double mass2  = 0.000511*0.000511;
                float  p2     = pow(gsf->p(), 2);
                float  energy = sqrt(mass2+p2);
                math::XYZTLorentzVector mom(gsf->px(), gsf->py(), gsf->pz(), energy);
                math::XYZTLorentzVector pos(gsf->vx(), gsf->vy(), gsf->vz(), 0.);

                BaseParticlePropagator propagator(RawParticle(mom, pos, gsf->charge()), 0., 0., 3.8);
                propagator.propagateToEcalEntrance(true);
                bool reach_ECAL = propagator.getSuccess();

                GlobalPoint ecal_pos(propagator.particle().x(), propagator.particle().y(), propagator.particle().z());

                //track-cluster matching for most energetic clusters
                sc_clus1_nxtal_  = -999.;
                sc_clus1_dphi_   = -999.;
                sc_clus1_deta_   = -999.;
                sc_clus1_E_      = -999.;
                sc_clus1_EoverP_ = -999.;
                sc_clus2_dphi_   = -999.;
                sc_clus2_deta_   = -999.;
                sc_clus2_E_      = -999.;
                sc_clus2_EoverP_ = -999.;

                //iterate through ECAL clusters and sort in energy
                int clusNum   = 0;
                float maxEne1 = -1;
                float maxEne2 = -1;
                int i1 = -1;
                int i2 = -1;
                //find energetic clusters
                findEnergeticClusters(sc, clusNum, maxEne1, maxEne2, i1, i2);

                //track-clusters match
                clusNum=0;
                if(sc->clustersSize()>0 && sc->clustersBegin()!=sc->clustersEnd()){
                  for(auto const& cluster : sc->clusters()){
                    float deta = ecal_pos.eta() - cluster->eta();
                    float dphi = reco::deltaPhi(ecal_pos.phi(), cluster->phi());
                    if(clusNum == i1){
                      sc_clus1_E_ = cluster->energy();
                      if(gsf->pMode()>0){sc_clus1_EoverP_ = cluster->energy() / gsf->pMode();}
                      sc_clus1_nxtal_ = (float)cluster->size();
                      if(reach_ECAL>0){
                        sc_clus1_deta_ = deta;
                        sc_clus1_dphi_ = dphi;
                      }
                    }
                    else if(clusNum==i2){
                      sc_clus2_E_ = cluster->energy();
                      if(gsf->pMode()>0){sc_clus2_EoverP_ = cluster->energy() / gsf->pMode();}
                      if(reach_ECAL>0){
                        sc_clus2_deta_ = deta;
                        sc_clus2_dphi_ = dphi;
                      }
                    }
                    clusNum++;
                  }
                }
            }
        }
        else{
            gsf_mode_p_  = -999.;
            gsf_chi2red_ = -999.; 
            gsf_nhits_   = -999.;
            gsf_dr_      = -999.;
        }
    }
    else{
        gsf_mode_p_  = -999.;
        gsf_chi2red_ = -999.; 
        gsf_nhits_   = -999.;
        gsf_dr_      = -999.;
    }

    features.push_back(gsf_mode_p_);
    features.push_back(gsf_chi2red_);
    features.push_back(gsf_dr_);
    features.push_back(gsf_nhits_);

    features.push_back(sc_clus1_nxtal_);
    features.push_back(sc_clus1_dphi_);
    features.push_back(sc_clus1_deta_);
    features.push_back(sc_clus1_E_);
    features.push_back(sc_clus1_EoverP_);

    features.push_back(sc_clus2_dphi_);
    features.push_back(sc_clus2_deta_);
    features.push_back(sc_clus2_E_);
    features.push_back(sc_clus2_EoverP_);   

    ids.push_back(forest_->GetResponse(features.data()));
    
    if(isMC_ && doMatch_){matchedToGenEle.push_back(matchToTruth(ele, *genParticles));}

  } // end loop through reco electrons

  auto idMap = std::make_unique<edm::ValueMap<float>>();
  edm::ValueMap<float>::Filler fillerID(*idMap);
  fillerID.insert(edm::RefProd<std::vector<pat::Electron>>(electrons), ids.begin(), ids.end());
  fillerID.fill();
  iEvent.put(std::move(idMap), "ids");

  if(isMC_ && doMatch_){
    auto matchMap = std::make_unique<edm::ValueMap<int>>();
    edm::ValueMap<int>::Filler fillerMatch(*matchMap);
    fillerMatch.insert(edm::RefProd<std::vector<pat::Electron>>(electrons), matchedToGenEle.begin(), matchedToGenEle.end());
    fillerMatch.fill();
    iEvent.put(std::move(matchMap), "matchedToGenEle");
  }
}

int lowPtIDProducer::matchToTruth(reco::GsfElectron const& recoEle,
                                  edm::View<reco::GenParticle> const& genParticles) const{
  //Explicit loop and geometric matching method
  double dR = 999.;
  reco::GenParticle const* closestGen = nullptr;
  
  for(auto const& genPart : genParticles){
    //drop everything that is not an electron or not status 1
    if(std::abs(genPart.pdgId())!=11 || genPart.status()!=1){continue;}

    double dRtmp = ROOT::Math::VectorUtil::DeltaR(recoEle.p4(), genPart.p4());
    if(dRtmp<dR){
      dR=dRtmp;
      closestGen = &genPart;
    }
  }
  //See if closest electron is close enough. If not, no match found.
  if(closestGen == nullptr || dR >= deltaR_){
    return UNMATCHED;
  }
  if(closestGen->fromHardProcessFinalState() || closestGen->isPromptFinalState()){return TRUE_PROMPT_ELECTRON;}
  if(closestGen->isDirectHardProcessTauDecayProductFinalState()){return TRUE_ELECTRON_FROM_TAU;}
  return TRUE_NON_PROMPT_ELECTRON;
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void lowPtIDProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  edm::ParameterSetDescription desc;
  desc.add<edm::InputTag>("src", edm::InputTag("slimmedLowPtElectrons"));
  desc.add<edm::InputTag>("rho", edm::InputTag("fixedGridRhoFastjetAll"));
  desc.add<edm::InputTag>("genParticles", edm::InputTag("prunedGenParticles"));
  desc.add<std::string>("modelFile", "");
  desc.add<bool>("isMC", false);
  desc.add<bool>("doMatch", false);
  desc.add<double>("deltaR", 0.03);
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(lowPtIDProducer);
