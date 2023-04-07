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

void guadagnoMC(){

std::ifstream file("../dati/guadagnoMC.txt");

double Vin,fsVin,Vout,fsVout;

TGraphErrors* g1 = new TGraphErrors;
TF1* f = new TF1("f","[0]+x*[1]");
//f->SetParameters();

for(int i=0; file>>Vin>>fsVin>>Vout>>fsVout; i++){
 double eVin, eVout;
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
g1->SetPoint(i,Vin,Vout);
g1->SetPointError(i,eVin,eVout);

}

TCanvas* c1 = new TCanvas("","",800,600);
c1->cd();

g1->Fit("f");
g1->Draw("ap");
g1->SetTitle("Fit G_MC;V_in[V];V_out[V]");
gStyle->SetOptFit();
c1->SaveAs("..figure/guadagnoMC.pdf");

double q = f->GetParameter(0);
double G = f->GetParameter(1);

double eq = f->GetParError(0);
double eG = f->GetParError(1);

std::cout<<"quota = "<<q<<" +/- "<<eq<<std::endl;
std::cout<<"G_MC = "<<G<<" +/- "<<eG<<std::endl;
}