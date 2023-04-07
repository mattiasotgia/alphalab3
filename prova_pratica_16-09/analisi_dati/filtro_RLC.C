#include<vector>
#include<cmath>
#include<iostream>
#include<fstream>
#include<string>

#include<TCanvas.h>
#include<TGraphErrors.h>
#include<TF1.h>
#include<TStyle.h>
#include<TAxis.h>
#include<TMath.h>
#include<TLatex.h>
#include<TLegend.h>

double get_VRangeErr(double errPercent, int partitions, double range1){ 
  return errPercent * partitions *  range1;
}
double get_TRangeErr(double range1, double errPercent = 0.0016, int partition = 10){
    return range1 * errPercent * partition;
}

double getH(double vin, double vout){
    return vout / vin;
}

double get_HErr(double Vin, double Vout, double eVin, double eVout){ 
  return sqrt(pow(eVout / Vin, 2) + pow(eVin * Vout / pow(Vin, 2), 2));
}

double get_phi(double T, double dt){
    return 2 * M_PI * dt / T;
}

double get_phiErr(double T, double dt, double eT, double edt){
    return 2 * M_PI * sqrt(pow(edt/T, 2) + pow(dt * eT/(pow(T, 2)), 2));
}

void filtro_RLC(){

std::ifstream file ("../dati/filtro_RLC.txt");

double Vin,Vout,T,dT,fsVin,fsVout,fsT,fsdT;

TCanvas* c1 = new TCanvas("c1", "", 600, 600);
TCanvas* c2 = new TCanvas("c2", "", 600, 600);
TGraphErrors* g1 = new TGraphErrors;
TGraphErrors* g2 = new TGraphErrors;

TF1* fit_bode = new TF1("fit_bode","1/sqrt(1+[1]*pow((pow(x,2)-pow([0],2))/([0]*x),2))");  //[0]=nu_0 [1]=Q^2
fit_bode->SetParName(0,"v_0");
fit_bode->SetParName(1,"Q^2");
fit_bode->SetParameters(3200,2);

TF1* fit_fase = new TF1("fit_fase","-atan(([1]*(x*x-[0]*[0]))/([0]*x))"); //[0]=nu0 [1]=Q
fit_fase->SetParName(0,"v_0");
fit_fase->SetParName(1,"Q");
fit_fase->SetParameters(3200,2);

for (int i=0; file>>Vin>>fsVin>>Vout>>fsVout>>T>>fsT>>dT>>fsdT; i++){
double eVin,eVout,eT,edT;
if (fsVin<0.01){
        eVin=get_VRangeErr(0.04,8,fsVin)/sqrt(3);
        }
    else{
        eVin=get_VRangeErr(0.03,8,fsVin)/sqrt(3);
        }
    if(fsVout<0.01){
        eVout=get_VRangeErr(0.04,8,fsVout)/sqrt(3);
    }
    else{
        eVout=get_VRangeErr(0.03,8,fsVout)/sqrt(3);
    }

    eT=get_TRangeErr(fsT);
    edT=get_TRangeErr(fsT);
    double H=getH(Vin,Vout);
    double eH=get_HErr(Vin,Vout,eVin,eVout);
    double phi=get_phi(T,dT);
    double ephi=get_phiErr(T,dT,eT,edT);

    g1->SetPoint(i,1/T,H);
    g1->SetPointError(i,eT/(pow(T,2)),eH);

    g2->SetPoint(i, 1 / T, phi);
    g2->SetPointError(i, eT/pow(T, 2), ephi);

}


c1->cd();
c1->SetLogx();
g1->Fit("fit_bode");
g1->Draw("ap");
g1->SetTitle("Bode |H|;1/T[Hz];|H|");
gStyle->SetOptFit();
c1->SaveAs("../figure/RLC_bode_H.pdf");

c2->cd();
c2->SetLogx();
g2->Fit("fit_fase");
g2->Draw("ap");
g2->SetTitle("Bode fase;1/T[Hz];Beta[rad]");
gStyle->SetOptFit();
c2->SaveAs("../figure/RLC_bode_fase.pdf");

double nu0_b = fit_bode->GetParameter(0);
double e_nu0_b = fit_bode->GetParError(0);
double nu0_f = fit_fase->GetParameter(0);
double e_nu0_f = fit_fase->GetParError(0);

double Q_b = sqrt(fit_bode->GetParameter(1));
double e_Qb = 2*Q_b*(fit_bode->GetParError(1));
double Q_f = fit_fase->GetParameter(1);
double e_Qf = fit_fase->GetParError(1);

double best_value_nu0 = (nu0_b/pow(e_nu0_b,2)+nu0_f/pow(e_nu0_f,2))/(1/pow(e_nu0_b,2)+1/pow(e_nu0_f,2));
double e_b_v_nu0 = sqrt((pow(e_nu0_b,2)*pow(e_nu0_f,2))/(pow(e_nu0_b,2)+pow(e_nu0_f,2)));

if(abs(nu0_b-nu0_f) < 3*sqrt(pow(e_nu0_b,2)+pow(e_nu0_f,2))){
    std::cout<<"I valori dei parametri v_0 sono compatibili e la miglior stima è:"<<best_value_nu0<<" +/- "<<e_b_v_nu0<<std::endl;
}
else{
    std::cout<<"I due valori di v_0 non sono compatibili"<<std::endl;
}

double best_value_Q = (Q_b/pow(e_Qb,2)+Q_f/pow(e_Qf,2))/(1/pow(e_Qb,2)+1/pow(e_Qf,2));
double e_b_v_Q = sqrt((pow(e_Qb,2)*pow(e_Qf,2))/(pow(e_Qb,2)+pow(e_Qf,2)));

if(abs(Q_b-Q_f) < 3*sqrt(pow(e_Qb,2)+pow(e_Qf,2))){
    std::cout<<"I valori dei parametri Q sono compatibili e la miglior stima è:"<<best_value_Q<<" +/- "<<e_b_v_Q<<std::endl;
}
else{
    std::cout<<"I due valori di Q non sono compatibili"<<std::endl;
}

}