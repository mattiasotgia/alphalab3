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

void filtro_passa_basso_attivo(){

std::ifstream file ("../dati/filtro_passa_basso_attivo.txt");

double Vin,Vout,T,dT,fsVin,fsVout,fsT,fsdT;

TCanvas* c1 = new TCanvas("c1", "", 600, 600);
TCanvas* c2 = new TCanvas("c2", "", 600, 600);
TGraphErrors* g1 = new TGraphErrors;
TGraphErrors* g2 = new TGraphErrors;

TF1* fit_bode = new TF1("fit_bode","[0]/sqrt(pow(x,2)/[1]+1)");  //[0]=G [1]=nu_0^2
fit_bode->SetParName(0,"G");
fit_bode->SetParName(1,"v_0^2");
//fit_bode->SetParameters();
TF1* fit_fase = new TF1("fit_fase","-atan(x/[0])"); //[0]=nu_0
fit_fase->SetParName(0,"v_0");
//fit_fase->SetParameter(0,?);

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
c1->SaveAs("../figure/passabasso_attivo_bode_H.pdf");

c2->cd();
c2->SetLogx();
g2->Fit("fit_fase");
g2->Draw("ap");
g2->SetTitle("Bode Fase;1/T[Hz];Beta");
gStyle->SetOptFit();
c2->SaveAs("../figure/passabasso_attivo_bode_fase.pdf");

double nu0_b2 = fit_bode->GetParameter(1);
double nu0_b = sqrt(nu0_b2);
double e_par = fit_bode->GetParError(1);
double e_nu0_b = 2*nu0_b*e_par;
double nu0_f = fit_fase->GetParameter(0);
double e_nu0_f = fit_fase->GetParError(0);

double best_value = (nu0_b/pow(e_nu0_b,2)+nu0_f/pow(e_nu0_f,2))/(1/pow(e_nu0_b,2)+1/pow(e_nu0_f,2));
double e_b_v = sqrt((pow(e_nu0_b,2)*pow(e_nu0_f,2))/(pow(e_nu0_b,2)+pow(e_nu0_f,2)));

if(abs(nu0_b-nu0_f) < 3*sqrt(pow(e_nu0_b,2)+pow(e_nu0_f,2))){
    std::cout<<"I valori dei parametri sono compatibili e la miglior stima è:"<<best_value<<" +/- "<<e_b_v<<std::endl;
}
else{
    std::cout<<"I due valori non sono compatibili"<<std::endl;
}


}