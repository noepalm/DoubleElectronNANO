#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"

#include <vector>
#include <memory>
#include <map>
#include <string>
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"
#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "DataFormats/PatCandidates/interface/CompositeCandidate.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "CommonTools/Statistics/interface/ChiSquaredProbability.h"
#include "helper.h"
#include <limits>
#include <algorithm>
#include "KinVtxFitter.h"
#include <TLorentzVector.h>

class BToKLLBuilder : public edm::global::EDProducer<> {

  // perhaps we need better structure here (begin run etc)
public:
  typedef std::vector<reco::TransientTrack> TransientTrackCollection;

  explicit BToKLLBuilder(const edm::ParameterSet &cfg):
    bFieldToken_(esConsumes<MagneticField, IdealMagneticFieldRecord>()),
    //ttbToken_(esConsumes<TransientTrackBuilder, TransientTrackRecord>()),
    k_selection_{cfg.getParameter<std::string>("kaonSelection")},
    filter_by_selection_{cfg.getParameter<bool>("filterBySelection")},
    pre_vtx_selection_{cfg.getParameter<std::string>("preVtxSelection")},
    post_vtx_selection_{cfg.getParameter<std::string>("postVtxSelection")},
    dileptons_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("dileptons") )},
    dileptons_kinVtxs_{consumes<std::vector<KinVtxFitter> >( cfg.getParameter<edm::InputTag>("dileptonKinVtxs") )},
    leptons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("leptonTransientTracks") )},
    kaons_{consumes<pat::CompositeCandidateCollection>( cfg.getParameter<edm::InputTag>("kaons") )},
    kaons_ttracks_{consumes<TransientTrackCollection>( cfg.getParameter<edm::InputTag>("kaonsTransientTracks") )},
    isotracksToken_(consumes<pat::PackedCandidateCollection>(cfg.getParameter<edm::InputTag>("tracks"))),
    isolostTracksToken_(consumes<pat::PackedCandidateCollection>(cfg.getParameter<edm::InputTag>("lostTracks"))),
    isotrk_selection_{cfg.getParameter<std::string>("isoTracksSelection")},
    isotrk_dca_selection_{cfg.getParameter<std::string>("isoTracksDCASelection")},
    isotrkDCACut_(cfg.getParameter<double>("isotrkDCACut")),
    isotrkDCATightCut_(cfg.getParameter<double>("isotrkDCATightCut")),
    drIso_cleaning_(cfg.getParameter<double>("drIso_cleaning")),
    beamspot_{consumes<reco::BeamSpot>( cfg.getParameter<edm::InputTag>("beamSpot") )},
    vertex_src_{consumes<reco::VertexCollection>( cfg.getParameter<edm::InputTag>("offlinePrimaryVertexSrc") )}
    {
      produces<pat::CompositeCandidateCollection>();
    }

  ~BToKLLBuilder() override {}
  
  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}
  
private:
  const edm::ESGetToken<MagneticField, IdealMagneticFieldRecord> bFieldToken_;
  //const edm::ESGetToken<TransientTrackBuilder, TransientTrackRecord> ttbToken_;
  const StringCutObjectSelector<pat::CompositeCandidate> k_selection_; 
  const bool filter_by_selection_;
  const StringCutObjectSelector<pat::CompositeCandidate> pre_vtx_selection_; // cut on the di-lepton before the SV fit
  const StringCutObjectSelector<pat::CompositeCandidate> post_vtx_selection_; // cut on the di-lepton after the SV fit

  const edm::EDGetTokenT<pat::CompositeCandidateCollection> dileptons_;
  const edm::EDGetTokenT<std::vector<KinVtxFitter> > dileptons_kinVtxs_;
  const edm::EDGetTokenT<TransientTrackCollection> leptons_ttracks_;
  const edm::EDGetTokenT<pat::CompositeCandidateCollection> kaons_;
  const edm::EDGetTokenT<TransientTrackCollection> kaons_ttracks_;

  const edm::EDGetTokenT<pat::PackedCandidateCollection> isotracksToken_;
  const edm::EDGetTokenT<pat::PackedCandidateCollection> isolostTracksToken_;
  const StringCutObjectSelector<pat::PackedCandidate> isotrk_selection_; 
  const StringCutObjectSelector<pat::CompositeCandidate> isotrk_dca_selection_; 
  const double isotrkDCACut_;
  const double isotrkDCATightCut_;
  const double drIso_cleaning_;

  const edm::EDGetTokenT<reco::BeamSpot> beamspot_;  
  const edm::EDGetTokenT<reco::VertexCollection> vertex_src_;
};

void BToKLLBuilder::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const &iSetup) const {

  //input
  edm::Handle<pat::CompositeCandidateCollection> dileptons;
  evt.getByToken(dileptons_, dileptons);
  
  edm::Handle<std::vector<KinVtxFitter> > dileptons_kinVtxs;
  evt.getByToken(dileptons_kinVtxs_, dileptons_kinVtxs);

  edm::Handle<TransientTrackCollection> leptons_ttracks;
  evt.getByToken(leptons_ttracks_, leptons_ttracks);

  edm::Handle<pat::CompositeCandidateCollection> kaons;
  evt.getByToken(kaons_, kaons);
  
  edm::Handle<TransientTrackCollection> kaons_ttracks;
  evt.getByToken(kaons_ttracks_, kaons_ttracks);  

  edm::Handle<reco::BeamSpot> beamspot;
  evt.getByToken(beamspot_, beamspot);  

  edm::Handle<reco::VertexCollection> pvtxs;
  evt.getByToken(vertex_src_, pvtxs);

  const auto& bField = iSetup.getData(bFieldToken_);
  AnalyticalImpactPointExtrapolator extrapolator(&bField);

  //const auto& theB = iSetup.getData(ttbToken_);

  //for isolation
  edm::Handle<pat::PackedCandidateCollection> iso_tracks;
  evt.getByToken(isotracksToken_, iso_tracks);
  edm::Handle<pat::PackedCandidateCollection> iso_lostTracks;
  evt.getByToken(isolostTracksToken_, iso_lostTracks);
  unsigned int nTracks     = iso_tracks->size();
  unsigned int totalTracks = nTracks + iso_lostTracks->size();

  std::vector<int> used_lep1_id, used_lep2_id, used_trk_id;


  // output
  std::unique_ptr<pat::CompositeCandidateCollection> ret_val(new pat::CompositeCandidateCollection());
  
  for(size_t k_idx = 0; k_idx < kaons->size(); ++k_idx) {
    edm::Ptr<pat::CompositeCandidate> k_ptr(kaons, k_idx);
    if( !k_selection_(*k_ptr) ) continue;
    
    math::PtEtaPhiMLorentzVector k_p4(
      k_ptr->pt(), 
      k_ptr->eta(),
      k_ptr->phi(),
      K_MASS
      );

    for(size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
      edm::Ptr<pat::CompositeCandidate> ll_prt(dileptons, ll_idx);
      edm::Ptr<reco::Candidate> l1_ptr = ll_prt->userCand("l1");
      edm::Ptr<reco::Candidate> l2_ptr = ll_prt->userCand("l2");
      int l1_idx = ll_prt->userInt("l1_idx");
      int l2_idx = ll_prt->userInt("l2_idx");
    
      pat::CompositeCandidate cand;
      cand.setP4(ll_prt->p4() + k_p4);
      cand.setCharge(ll_prt->charge() + k_ptr->charge());
      // Use UserCands as they should not use memory but keep the Ptr itself
      // Put the lepton passing the corresponding selection
      cand.addUserCand("l1", l1_ptr);
      cand.addUserCand("l2", l2_ptr);
      cand.addUserCand("K", k_ptr);
      cand.addUserCand("dilepton", ll_prt);

      cand.addUserInt("l1_idx", l1_idx);
      cand.addUserInt("l2_idx", l2_idx);
      cand.addUserInt("k_idx", k_idx);
    
      auto dr_info = min_max_dr({l1_ptr, l2_ptr, k_ptr});
      cand.addUserFloat("min_dr", dr_info.first);
      cand.addUserFloat("max_dr", dr_info.second);
      // TODO add meaningful variables
      
      bool pre_vtx_sel = pre_vtx_selection_(cand);
      cand.addUserInt("pre_vtx_sel",pre_vtx_sel);
      if( filter_by_selection_ && !pre_vtx_sel ) continue;
    
      KinVtxFitter fitter(
        {leptons_ttracks->at(l1_idx), leptons_ttracks->at(l2_idx), kaons_ttracks->at(k_idx)},
        {l1_ptr->mass(), l2_ptr->mass(), K_MASS},
        {LEP_SIGMA, LEP_SIGMA, K_SIGMA} //some small sigma for the lepton mass
        );
      if(!fitter.success()) continue; // hardcoded, but do we need otherwise?
      cand.setVertex( 
        reco::Candidate::Point( 
          fitter.fitted_vtx().x(),
          fitter.fitted_vtx().y(),
          fitter.fitted_vtx().z()
          )  
        );
      used_lep1_id.emplace_back(l1_idx);
      used_lep2_id.emplace_back(l2_idx);
      used_trk_id.emplace_back(k_idx);
      cand.addUserInt("sv_OK" , fitter.success());
      cand.addUserFloat("sv_chi2", fitter.chi2());
      cand.addUserFloat("sv_ndof", fitter.dof()); // float??
      cand.addUserFloat("sv_prob", fitter.prob());
      cand.addUserFloat("fitted_mll" , (fitter.daughter_p4(0) + fitter.daughter_p4(1)).mass());
      auto fit_p4 = fitter.fitted_p4();
      cand.addUserFloat("fitted_pt"  , fit_p4.pt()); 
      cand.addUserFloat("fitted_eta" , fit_p4.eta());
      cand.addUserFloat("fitted_phi" , fit_p4.phi());
      cand.addUserFloat("fitted_mass", fitter.fitted_candidate().mass());      
      cand.addUserFloat("fitted_massErr", sqrt(fitter.fitted_candidate().kinematicParametersError().matrix()(6,6)));      
      cand.addUserFloat(
        "cos_theta_2D", 
        cos_theta_2D(fitter, *beamspot, cand.p4())
        );
      cand.addUserFloat(
        "fitted_cos_theta_2D", 
        cos_theta_2D(fitter, *beamspot, fit_p4)
        );
      auto lxy = l_xy(fitter, *beamspot);
      cand.addUserFloat("l_xy", lxy.value());
      cand.addUserFloat("l_xy_unc", lxy.error());
      cand.addUserFloat("vtx_x", cand.vx());
      cand.addUserFloat("vtx_y", cand.vy());
      cand.addUserFloat("vtx_z", cand.vz());
      cand.addUserFloat("vtx_ex", sqrt(fitter.fitted_vtx_uncertainty().cxx()));
      cand.addUserFloat("vtx_ey", sqrt(fitter.fitted_vtx_uncertainty().cyy()));
      cand.addUserFloat("vtx_ez", sqrt(fitter.fitted_vtx_uncertainty().czz()));

      cand.addUserFloat("fitted_l1_pt" , fitter.daughter_p4(0).pt()); 
      cand.addUserFloat("fitted_l1_eta", fitter.daughter_p4(0).eta());
      cand.addUserFloat("fitted_l1_phi", fitter.daughter_p4(0).phi());
      cand.addUserFloat("fitted_l2_pt" , fitter.daughter_p4(1).pt()); 
      cand.addUserFloat("fitted_l2_eta", fitter.daughter_p4(1).eta());
      cand.addUserFloat("fitted_l2_phi", fitter.daughter_p4(1).phi());
      cand.addUserFloat("fitted_k_pt"  , fitter.daughter_p4(2).pt()); 
      cand.addUserFloat("fitted_k_eta" , fitter.daughter_p4(2).eta());
      cand.addUserFloat("fitted_k_phi" , fitter.daughter_p4(2).phi());

      // Anti-Do variables
      // From: https://github.com/gkaratha/cmgtools-lite/blob/1d02c82/RKAnalysis/python/tools/nanoAOD/UserFunctions.py#L382-L395
      TLorentzVector lep;
      if ( fitter.fitted_daughter(0).particleCharge() != fitter.fitted_daughter(2).particleCharge() ) {
	lep.SetPtEtaPhiM( fitter.daughter_p4(0).Pt(),
			  fitter.daughter_p4(0).Eta(),
			  fitter.daughter_p4(0).Phi(),
			  0.493); // Kaon mass
      } else {//if ( fitter.fitted_daughter(1).particleCharge() != fitter.fitted_daughter(2).particleCharge() ) {
	lep.SetPtEtaPhiM( fitter.daughter_p4(1).Pt(),
			  fitter.daughter_p4(1).Eta(),
			  fitter.daughter_p4(1).Phi(),
			  0.493); // Kaon mass
//      } else {
//	std::cerr << "Anti-D0 filter: Same-sign leptons?"
//		  << " lep1 charge=" << fitter.fitted_daughter(1).particleCharge()
//		  << " lep2 charge=" << fitter.fitted_daughter(1).particleCharge()
//		  << ". Assuming leading lepton takes kaon mass..."
//		  << std::endl;
//	lep.SetPtEtaPhiM( fitter.daughter_p4(0).Pt(),
//			  fitter.daughter_p4(0).Eta(),
//			  fitter.daughter_p4(0).Phi(),
//			  0.493); // Kaon mass
      }
      TLorentzVector kaon;
      kaon.SetPtEtaPhiM(fitter.daughter_p4(2).Pt(),
			fitter.daughter_p4(2).Eta(),
			fitter.daughter_p4(2).Phi(),
			0.139); // Pion mass
      float mass1 = (lep+kaon).M(); // mass(K-->pi,e-->K)
      lep.SetPtEtaPhiM(lep.Pt(),lep.Eta(),lep.Phi(),0.139); // Pion mass
      kaon.SetPtEtaPhiM(kaon.Pt(),kaon.Eta(),kaon.Phi(),0.493); // Kaon mass
      float mass2 = (lep+kaon).M(); // mass(K-->K,e-->pi)
      cand.addUserFloat("D0_mass_LepToK_KToPi",mass1);
      cand.addUserFloat("D0_mass_LepToPi_KToK",mass2);

      // kaon 3D impact parameter from dilepton SV
      TrajectoryStateOnSurface tsos = extrapolator.extrapolate(kaons_ttracks->at(k_idx).impactPointState(), dileptons_kinVtxs->at(ll_idx).fitted_vtx());
      std::pair<bool,Measurement1D> cur2DIP = signedTransverseImpactParameter(tsos, dileptons_kinVtxs->at(ll_idx).fitted_refvtx(), *beamspot);
      std::pair<bool,Measurement1D> cur3DIP = signedImpactParameter3D(tsos, dileptons_kinVtxs->at(ll_idx).fitted_refvtx(), *beamspot, (*pvtxs)[0].position().z());

      cand.addUserFloat("k_svip2d" , cur2DIP.second.value());
      cand.addUserFloat("k_svip2d_err" , cur2DIP.second.error());
      cand.addUserFloat("k_svip3d" , cur3DIP.second.value());
      cand.addUserFloat("k_svip3d_err" , cur3DIP.second.error());

      bool post_vtx_sel = post_vtx_selection_(cand);
      cand.addUserInt("post_vtx_sel",post_vtx_sel);
      if( filter_by_selection_ && !post_vtx_sel ) continue;

      //compute isolation
      float l1_iso03 = 0;
      float l1_iso04 = 0;
      float l2_iso03 = 0;
      float l2_iso04 = 0;
      float k_iso03  = 0;
      float k_iso04  = 0;
      float b_iso03  = 0;
      float b_iso04  = 0;
      int l1_n_isotrk = 0;
      int l2_n_isotrk = 0;
      int k_n_isotrk = 0;
      int b_n_isotrk = 0;

      for( unsigned int iTrk=0; iTrk<totalTracks; ++iTrk ) {
      
        const pat::PackedCandidate & trk = (iTrk < nTracks) ? (*iso_tracks)[iTrk] : (*iso_lostTracks)[iTrk-nTracks];
        // define selections for iso tracks (pT, eta, ...)
        if( !isotrk_selection_(trk) ) continue;
        // check if the track is the kaon
        if (k_ptr->userCand("cand") ==  edm::Ptr<reco::Candidate> ( iso_tracks, iTrk ) ) continue;
        // check if the track is one of the two leptons
        if (track_to_lepton_match(l1_ptr, iso_tracks.id().id(), iTrk) ||
            track_to_lepton_match(l2_ptr, iso_tracks.id().id(), iTrk) ) continue;
        // cross clean leptons
        // hard to trace the source particles of low-pT electron in B builder
        // use simple dR cut instead
        float dr_to_l1_prefit = deltaR(l1_ptr->eta(), l1_ptr->phi(), trk.eta(), trk.phi());
        float dr_to_l2_prefit = deltaR(l2_ptr->eta(), l2_ptr->phi(), trk.eta(), trk.phi());
        if ((dr_to_l1_prefit < drIso_cleaning_) || (dr_to_l2_prefit < drIso_cleaning_)) continue;

        // add to final particle iso if dR < cone
        float dr_to_l1 = deltaR(cand.userFloat("fitted_l1_eta"), cand.userFloat("fitted_l1_phi"), trk.eta(), trk.phi());
        float dr_to_l2 = deltaR(cand.userFloat("fitted_l2_eta"), cand.userFloat("fitted_l2_phi"), trk.eta(), trk.phi());
        float dr_to_k  = deltaR(cand.userFloat("fitted_k_eta") , cand.userFloat("fitted_k_phi") , trk.eta(), trk.phi());
        float dr_to_b  = deltaR(cand.userFloat("fitted_eta")   , cand.userFloat("fitted_phi") , trk.eta(), trk.phi());

        if (dr_to_l1 < 0.4){
          l1_iso04 += trk.pt();
          l1_n_isotrk++;
          if ( dr_to_l1 < 0.3) l1_iso03 += trk.pt();
        }
        if (dr_to_l2 < 0.4){
          l2_iso04 += trk.pt();
          l2_n_isotrk++;
          if (dr_to_l2 < 0.3)  l2_iso03 += trk.pt();
        }
        if (dr_to_k < 0.4){
          k_iso04 += trk.pt();
          k_n_isotrk++;
          if (dr_to_k < 0.3) k_iso03 += trk.pt();
        }
        if (dr_to_b < 0.4){
          b_iso04 += trk.pt();
          b_n_isotrk++;
          if (dr_to_b < 0.3) b_iso03 += trk.pt();
        }
      }

      //compute isolation from surrounding tracks only
      float l1_iso03_dca = 0;
      float l1_iso04_dca = 0;
      float l2_iso03_dca = 0;
      float l2_iso04_dca = 0;
      float k_iso03_dca  = 0;
      float k_iso04_dca  = 0;
      float b_iso03_dca  = 0;
      float b_iso04_dca  = 0;
      int l1_n_isotrk_dca = 0;
      int l2_n_isotrk_dca = 0;
      int k_n_isotrk_dca = 0;
      int b_n_isotrk_dca = 0;

      float l1_iso03_dca_tight = 0;
      float l1_iso04_dca_tight = 0;
      float l2_iso03_dca_tight = 0;
      float l2_iso04_dca_tight = 0;
      float k_iso03_dca_tight  = 0;
      float k_iso04_dca_tight  = 0;
      float b_iso03_dca_tight  = 0;
      float b_iso04_dca_tight  = 0;
      int l1_n_isotrk_dca_tight = 0;
      int l2_n_isotrk_dca_tight = 0;
      int k_n_isotrk_dca_tight = 0;
      int b_n_isotrk_dca_tight = 0;

      for(size_t trk_idx = 0; trk_idx < kaons->size(); ++trk_idx) {
        // corss clean kaon
        if (trk_idx == k_idx) continue;
        edm::Ptr<pat::CompositeCandidate> trk_ptr(kaons, trk_idx);
        if( !isotrk_dca_selection_(*trk_ptr) ) continue;
        // cross clean PF (electron and muon)
        unsigned int iTrk = trk_ptr->userInt("keyPacked");
        if (track_to_lepton_match(l1_ptr, iso_tracks.id().id(), iTrk) ||
            track_to_lepton_match(l2_ptr, iso_tracks.id().id(), iTrk) ) {
          continue;
        }
        // cross clean leptons
        // hard to trace the source particles of low-pT electron in B builder
        // use simple dR cut instead
        float dr_to_l1_prefit = deltaR(l1_ptr->eta(), l1_ptr->phi(), trk_ptr->eta(), trk_ptr->phi());
        float dr_to_l2_prefit = deltaR(l2_ptr->eta(), l2_ptr->phi(), trk_ptr->eta(), trk_ptr->phi());
        if ((dr_to_l1_prefit < drIso_cleaning_) || (dr_to_l2_prefit < drIso_cleaning_)) continue;

        TrajectoryStateOnSurface tsos_iso = extrapolator.extrapolate(kaons_ttracks->at(trk_idx).impactPointState(), fitter.fitted_vtx());
        std::pair<bool,Measurement1D> cur3DIP_iso = absoluteImpactParameter3D(tsos_iso, fitter.fitted_refvtx());
        float svip_iso = cur3DIP_iso.second.value();
        if (cur3DIP_iso.first && svip_iso < isotrkDCACut_) {
          // add to final particle iso if dR < cone
          float dr_to_l1 = deltaR(cand.userFloat("fitted_l1_eta"), cand.userFloat("fitted_l1_phi"), trk_ptr->eta(), trk_ptr->phi());
          float dr_to_l2 = deltaR(cand.userFloat("fitted_l2_eta"), cand.userFloat("fitted_l2_phi"), trk_ptr->eta(), trk_ptr->phi());
          float dr_to_k  = deltaR(cand.userFloat("fitted_k_eta") , cand.userFloat("fitted_k_phi") , trk_ptr->eta(), trk_ptr->phi());
          float dr_to_b  = deltaR(cand.userFloat("fitted_eta")   , cand.userFloat("fitted_phi") , trk_ptr->eta(), trk_ptr->phi());

          if (dr_to_l1 < 0.4){
            l1_iso04_dca += trk_ptr->pt();
            l1_n_isotrk_dca++;
            if (svip_iso < isotrkDCATightCut_) {
              l1_iso04_dca_tight += trk_ptr->pt();
              l1_n_isotrk_dca_tight++;
            }
            if (dr_to_l1 < 0.3) {
              l1_iso03_dca += trk_ptr->pt();
              if (svip_iso < isotrkDCATightCut_) {
                l1_iso03_dca_tight += trk_ptr->pt();
              }
            }
          }
          if (dr_to_l2 < 0.4){
            l2_iso04_dca += trk_ptr->pt();
            l2_n_isotrk_dca++;
            if (svip_iso < isotrkDCATightCut_) {
              l2_iso04_dca_tight += trk_ptr->pt();
              l2_n_isotrk_dca_tight++;
            }
            if (dr_to_l2 < 0.3) {
              l2_iso03_dca += trk_ptr->pt();
              if (svip_iso < isotrkDCATightCut_) {
                l2_iso03_dca_tight += trk_ptr->pt();
              }
            }
          }
          if (dr_to_k < 0.4){
            k_iso04_dca += trk_ptr->pt();
            k_n_isotrk_dca++;
            if (svip_iso < isotrkDCATightCut_) {
              k_iso04_dca_tight += trk_ptr->pt();
              k_n_isotrk_dca_tight++;
            }
            if (dr_to_k < 0.3) {
              k_iso03_dca += trk_ptr->pt();
              if (svip_iso < isotrkDCATightCut_) {
                k_iso03_dca_tight += trk_ptr->pt();
              }
            }
          }
          if (dr_to_b < 0.4){
            b_iso04_dca += trk_ptr->pt();
            b_n_isotrk_dca++;
            if (svip_iso < isotrkDCATightCut_) {
              b_iso04_dca_tight += trk_ptr->pt();
              b_n_isotrk_dca_tight++;
            }
            if (dr_to_b < 0.3) {
              b_iso03_dca += trk_ptr->pt();
              if (svip_iso < isotrkDCATightCut_) {
                b_iso03_dca_tight += trk_ptr->pt();
              }
            }
          }
        }
      }


      cand.addUserFloat("l1_iso03", l1_iso03);
      cand.addUserFloat("l1_iso04", l1_iso04);
      cand.addUserFloat("l2_iso03", l2_iso03);
      cand.addUserFloat("l2_iso04", l2_iso04);
      cand.addUserFloat("k_iso03" , k_iso03 );
      cand.addUserFloat("k_iso04" , k_iso04 );
      cand.addUserFloat("b_iso03" , b_iso03 );
      cand.addUserFloat("b_iso04" , b_iso04 );
      cand.addUserInt("l1_n_isotrk" , l1_n_isotrk);
      cand.addUserInt("l2_n_isotrk" , l2_n_isotrk);
      cand.addUserInt("k_n_isotrk" ,  k_n_isotrk);
      cand.addUserInt("b_n_isotrk" ,  b_n_isotrk);

      cand.addUserFloat("l1_iso03_dca", l1_iso03_dca);
      cand.addUserFloat("l1_iso04_dca", l1_iso04_dca);
      cand.addUserFloat("l2_iso03_dca", l2_iso03_dca);
      cand.addUserFloat("l2_iso04_dca", l2_iso04_dca);
      cand.addUserFloat("k_iso03_dca" , k_iso03_dca );
      cand.addUserFloat("k_iso04_dca" , k_iso04_dca );
      cand.addUserFloat("b_iso03_dca" , b_iso03_dca );
      cand.addUserFloat("b_iso04_dca" , b_iso04_dca );
      cand.addUserInt("l1_n_isotrk_dca" , l1_n_isotrk_dca);
      cand.addUserInt("l2_n_isotrk_dca" , l2_n_isotrk_dca);
      cand.addUserInt("k_n_isotrk_dca" ,  k_n_isotrk_dca);
      cand.addUserInt("b_n_isotrk_dca" ,  b_n_isotrk_dca);

      cand.addUserFloat("l1_iso03_dca_tight", l1_iso03_dca_tight);
      cand.addUserFloat("l1_iso04_dca_tight", l1_iso04_dca_tight);
      cand.addUserFloat("l2_iso03_dca_tight", l2_iso03_dca_tight);
      cand.addUserFloat("l2_iso04_dca_tight", l2_iso04_dca_tight);
      cand.addUserFloat("k_iso03_dca_tight" , k_iso03_dca_tight );
      cand.addUserFloat("k_iso04_dca_tight" , k_iso04_dca_tight );
      cand.addUserFloat("b_iso03_dca_tight" , b_iso03_dca_tight );
      cand.addUserFloat("b_iso04_dca_tight" , b_iso04_dca_tight );
      cand.addUserInt("l1_n_isotrk_dca_tight" , l1_n_isotrk_dca_tight);
      cand.addUserInt("l2_n_isotrk_dca_tight" , l2_n_isotrk_dca_tight);
      cand.addUserInt("k_n_isotrk_dca_tight" ,  k_n_isotrk_dca_tight);
      cand.addUserInt("b_n_isotrk_dca_tight" ,  b_n_isotrk_dca_tight);

      ret_val->push_back(cand);
    } // for(size_t ll_idx = 0; ll_idx < dileptons->size(); ++ll_idx) {
  } // for(size_t k_idx = 0; k_idx < kaons->size(); ++k_idx)

  for (auto & cand: *ret_val){
    cand.addUserInt("n_k_used", std::count(used_trk_id.begin(),used_trk_id.end(),cand.userInt("k_idx")));
    cand.addUserInt("n_l1_used", std::count(used_lep1_id.begin(),used_lep1_id.end(),cand.userInt("l1_idx"))+std::count(used_lep2_id.begin(),used_lep2_id.end(),cand.userInt("l1_idx")));
    cand.addUserInt("n_l2_used", std::count(used_lep1_id.begin(),used_lep1_id.end(),cand.userInt("l2_idx"))+std::count(used_lep2_id.begin(),used_lep2_id.end(),cand.userInt("l2_idx")));
  }

  evt.put(std::move(ret_val));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(BToKLLBuilder);
