import re, optparse
import os.path,sys
import argparse
from math import *
import ROOT
from array import array
ROOT.gROOT.SetBatch(True)

def seq(start, stop, step=1):
    n = int(round((stop - start)/float(step)))
    if n > 1:
        return([start + step*i for i in range(n+1)])
    elif n == 1:
        return([start])
    else:
        return([])

#####
def redrawBorder():
   # this little macro redraws the axis tick marks and the pad border lines.
   ROOT.gPad.Update();
   ROOT.gPad.RedrawAxis();
   l = ROOT.TLine()
   l.SetLineWidth(3)
   l.DrawLine(ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymin(), ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymin());
   l.DrawLine(ROOT.gPad.GetUxmax(), 0.0001, ROOT.gPad.GetUxmax(), ROOT.gPad.GetUymax());
   l.DrawLine(ROOT.gPad.GetUxmin(), 0.0001, ROOT.gPad.GetUxmin(), ROOT.gPad.GetUymax());
   l.DrawLine(ROOT.gPad.GetUxmin(), 0.0001, ROOT.gPad.GetUxmax(), 0.0001);

def getVals(fname):
    fIn = ROOT.TFile.Open(fname)
    tIn = fIn.Get('limit')
    if tIn.GetEntries() != 6:
        print "*** WARNING: cannot parse file", fname, "because nentries != 6"
        raise RuntimeError('cannot parse file')
    vals = []
    for i in range(0, tIn.GetEntries()):
        tIn.GetEntry(i)
        qe = tIn.quantileExpected
        lim = tIn.limit
        vals.append((qe,lim))
    return vals

################################################################################################
###########OPTIONS
parser = argparse.ArgumentParser(description='Command line parser of skim options')
parser.add_argument('--version', dest='version',help='version, e.g v8', required = True)
parser.add_argument('--mllp',    dest='mllp'   ,help='mllp value'  , required = True)
parser.add_argument('--ctau',    dest='ctau'   ,help='ctau'        , required = True)
parser.add_argument('--categ',   dest='categ'  ,action='store_true', help='Category result')
parser.add_argument('--unblind', dest='unblind',action='store_true', help='Unblind the observed')
parser.add_argument('--order', dest='order',help='LO or NLO cross section', required = True)

args = parser.parse_args()
parser.set_defaults(categ=False)
parser.set_defaults(unblind=False)
###########
###CREATE TAGS
mllp   = args.mllp
ctau   = args.ctau
categ  = args.categ
version= args.version
unblind= args.unblind
order  = args.order

#Plot it
c1 = ROOT.TCanvas("c1", "c1", 1300, 1000)
c1.SetFrameLineWidth(3)
c1.SetBottomMargin (0.15)
c1.SetRightMargin (0.05)
c1.SetLeftMargin (0.15)
c1.SetGridx()
c1.SetGridy()

mg = ROOT.TMultiGraph()
gr2sigma = ROOT.TGraphAsymmErrors()
gr1sigma = ROOT.TGraphAsymmErrors()
grexp = ROOT.TGraph()
grobs = ROOT.TGraph()
grexp_csc = ROOT.TGraph()
grexp_dt  = ROOT.TGraph()
grobs_csc = ROOT.TGraph()
grobs_dt  = ROOT.TGraph()

#Assign xs and masses
xsections = []
masses    = []  
if mllp=='2':
    masses     = [200,300,400,500,600,700,800]
    if order =='LO':
      xsections = [0.08865, 0.01927, 0.005932, 0.002232, 0.0009479, 0.0004374,0.0002139]
    if order == 'NLO':
      xsections = [1.050e-01, 2.288e-02, 7.154e-03, 2.700e-03, 1.163e-03, 5.446e-04,2.711e-04]
if mllp=='10':
    masses     = [300,700,1000]
    if order =='LO':
      xsections = [0.08865, 0.01927, 0.005932, 0.002232, 0.0009479, 0.0004374,0.0002139]
    if order == 'NLO':
      xsections = [2.288e-02, 5.446e-04, 7.604e-05]

#Get XS predicted for vll vs mass
n  = 9
x  = array('d', [200,         300,      400,      500,       600,       700,      800,     900,   1000])
y  = array('d', [0.08865, 0.01927, 0.005932, 0.002232, 0.0009479, 0.0004374,0.0002139,0.000122,0.00006])
if order =='LO':
      y  = array('d', [0.08865, 0.01927, 0.005932, 0.002232, 0.0009479, 0.0004374,0.0002139,0.000122,0.00006])
if order == 'NLO':
      y  = array('d', [1.050e-01, 2.288e-02, 7.154e-03, 2.700e-03, 1.163e-03, 5.446e-04,2.711e-04,1.410e-04,7.604e-05])

##print coupling_xs
ptsList = [] 

#fill out the arrays for limits
for k in range(0, len(masses) ):
    fname = "datacards_%s/cards_%i_%s/higgsCombine_%i_%s.AsymptoticLimits.mH120.root"%(version,masses[k],ctau,masses[k],ctau)
    if unblind==True: fname = "datacards_unblinded_%s/cards_%i_%s/higgsCombine_%i_%s.AsymptoticLimits.mH120.root"%(version,masses[k],ctau,masses[k],ctau)
    vals  = getVals(fname)
    xs    = xsections[k]
    obs   = 0.0 ## FIXME
    if unblind==True: obs= vals[5][1]*xs
    m2s_t = vals[0][1]*xs
    m1s_t = vals[1][1]*xs
    exp   = vals[2][1]*xs
    p1s_t = vals[3][1]*xs
    p2s_t = vals[4][1]*xs

    ## because the other code wants +/ sigma vars as deviations, without sign, from the centeal exp value...
    p2s  = p2s_t - exp
    p1s  = p1s_t - exp
    m2s  = exp - m2s_t
    m1s  = exp - m1s_t
    xval = masses[k]
    ptsList.append((xval, obs, exp, p2s, p1s, m1s, m2s))
ptsList.sort()
for ipt, pt in enumerate(ptsList):
    xval = pt[0]
    obs  = pt[1]
    exp  = pt[2]
    p2s  = pt[3]
    p1s  = pt[4]
    m1s  = pt[5]
    m2s  = pt[6]
    grexp.SetPoint(ipt, xval, exp)
    grobs.SetPoint(ipt, xval, obs)
    gr1sigma.SetPoint(ipt, xval, exp)
    gr2sigma.SetPoint(ipt, xval, exp)
    gr1sigma.SetPointError(ipt, 0,0,m1s,p1s)
    gr2sigma.SetPointError(ipt, 0,0,m2s,p2s)

if categ==True:
    ptsList_csc = []
    ptsList_dt  = []
    #CSC fill
    for j in range(0, len(masses) ):
        fname = "datacards_%s/cards_%s_%s/VLLModel_CSCB/higgsCombine_%s_%s.AsymptoticLimits.mH120.root"%(version,masses[j],ctau,masses[j],ctau)
        if unblind==True: fname = "datacards_unblinded_%s/cards_%s_%s/VLLModel_CSCU/higgsCombine_%s_%s.AsymptoticLimits.mH120.root"%(version,masses[j],ctau,masses[j],ctau)
        vals  = getVals(fname)
        xs    = xsections[j]
        obs   = 0.0 ## FIXME
        if unblind==True: obs = vals[5][1]*xs
        m2s_t = vals[0][1]*xs
        m1s_t = vals[1][1]*xs
        exp   = vals[2][1]*xs
        p1s_t = vals[3][1]*xs
        p2s_t = vals[4][1]*xs
        ## because the other code wants +/ sigma vars as deviations, without sign, from the centeal exp value...
        p2s  = p2s_t - exp
        p1s  = p1s_t - exp
        m2s  = exp - m2s_t
        m1s  = exp - m1s_t
        xval = masses[j]
        ptsList_csc.append((xval, obs, exp, p2s, p1s, m1s, m2s))    
    ptsList_csc.sort()
    for ipt, pt in enumerate(ptsList_csc):
        xval = pt[0]
        exp  = pt[2]
        obs  = pt[1]
        grobs_csc.SetPoint(ipt, xval, obs)
        grexp_csc.SetPoint(ipt, xval, exp)
    #DT fill
    for k in range(0, len(masses) ):
        fname = "datacards_%s/cards_%s_%s/VLLModel_DTU/higgsCombine_%s_%s.AsymptoticLimits.mH120.root"%(version,masses[k],ctau,masses[k],ctau)
        if unblind==True: fname = "datacards_unblinded_%s/cards_%s_%s/VLLModel_DTU/higgsCombine_%s_%s.AsymptoticLimits.mH120.root"%(version,masses[k],ctau,masses[k],ctau)
        vals  = getVals(fname)
        xs    = xsections[k]
        obs   = 0.0 ## FIXME
        if unblind==True: obs = vals[5][1]*xs
        m2s_t = vals[0][1]*xs
        m1s_t = vals[1][1]*xs
        exp   = vals[2][1]*xs
        p1s_t = vals[3][1]*xs
        p2s_t = vals[4][1]*xs
        ## because the other code wants +/ sigma vars as deviations, without sign, from the centeal exp value...
        p2s  = p2s_t - exp
        p1s  = p1s_t - exp
        m2s  = exp - m2s_t
        m1s  = exp - m1s_t
        xval = masses[k]
        ptsList_dt.append((xval, obs, exp, p2s, p1s, m1s, m2s))    
    ptsList_dt.sort()
    for ipt, pt in enumerate(ptsList_dt):
        xval = pt[0]
        exp  = pt[2]
        obs  = pt[1]
        grobs_dt.SetPoint(ipt, xval, obs)
        grexp_dt.SetPoint(ipt, xval, exp)
    #set styles
    grexp_csc.SetMarkerStyle(24)
    grexp_csc.SetMarkerColor(4)
    grexp_csc.SetMarkerSize(0.8)
    grexp_csc.SetLineColor(ROOT.kRed+2)
    grexp_csc.SetLineWidth(3)
    grexp_csc.SetLineStyle(2)
    grexp_csc.SetFillColor(0) 
    grexp_dt.SetMarkerStyle(24)
    grexp_dt.SetMarkerColor(4)
    grexp_dt.SetMarkerSize(0.8)
    grexp_dt.SetLineColor(ROOT.kGreen+2)
    grexp_dt.SetLineWidth(3)
    grexp_dt.SetLineStyle(2)
    grexp_dt.SetFillColor(0) 
    grobs_csc.SetLineColor(ROOT.kRed+2)
    grobs_csc.SetLineWidth(3)
    grobs_csc.SetMarkerColor(1)
    grobs_csc.SetMarkerStyle(20)
    grobs_csc.SetFillStyle(0)
    grobs_dt.SetLineColor(ROOT.kGreen+2)
    grobs_dt.SetLineWidth(3)
    grobs_dt.SetMarkerColor(1)
    grobs_dt.SetMarkerStyle(20)
    grobs_dt.SetFillStyle(0)

######## set styles
grexp.SetMarkerStyle(24)
grexp.SetMarkerColor(4)
grexp.SetMarkerSize(0.8)
grexp.SetLineColor(ROOT.kBlue+2)
grexp.SetLineWidth(3)
grexp.SetLineStyle(2)
grexp.SetFillColor(0)
grobs.SetLineColor(1)
if categ==True: grobs.SetLineColor(ROOT.kBlue+2)
grobs.SetLineWidth(3)
grobs.SetMarkerColor(1)
grobs.SetMarkerStyle(20)
grobs.SetFillStyle(0)
gr1sigma.SetMarkerStyle(0)
gr1sigma.SetMarkerColor(3)
gr1sigma.SetFillColor(ROOT.kGreen+1)
gr1sigma.SetLineColor(ROOT.kGreen+1)
gr1sigma.SetFillStyle(1001)
gr2sigma.SetMarkerStyle(0)
gr2sigma.SetMarkerColor(5)
gr2sigma.SetFillColor(ROOT.kOrange)
gr2sigma.SetLineColor(ROOT.kOrange)
gr2sigma.SetFillStyle(1001)

###########
legend = ROOT.TLegend(0,0,0,0)
legend.SetFillColor(ROOT.kWhite)
legend.SetBorderSize(0)
# legend
if categ==True:
   legend.SetX1(0.17284)
   legend.SetY1(0.730526)
   legend.SetX2(0.520062)
   legend.SetY2(0.88)
   legend.SetHeader('95% CL median expected upper limts')
   legend.AddEntry(grobs_csc, "CSC Category", "l")
   legend.AddEntry(grobs_dt, "DT Category", "l")
   legend.AddEntry(grobs, "Combination", "l")
   fakePlot3 = ROOT.TGraphAsymmErrors()
   fakePlot3.SetFillColor(6)
   fakePlot3.SetFillStyle(3001)
   fakePlot3.SetLineColor(6)
   fakePlot3.SetLineWidth(3)
   if order == 'NLO': legend.AddEntry(fakePlot3, "NLO Theoretical prediction", "l")
   else: legend.AddEntry(fakePlot3, "Theoretical prediction", "l")
else:
   legend.SetX1(0.17284)
   legend.SetY1(0.630526+0.05)
   legend.SetX2(0.520062)
   legend.SetY2(0.88)
   legend.SetHeader('95% CL upper limits')
   if unblind==True: legend.AddEntry(grobs,"Observed","l")
   legend.AddEntry(grexp, "Median expected", "l")
   legend.AddEntry(gr1sigma, "68% expected", "f")
   legend.AddEntry(gr2sigma, "95% expected", "f")
   fakePlot3 = ROOT.TGraphAsymmErrors()
   fakePlot3.SetFillColor(6)
   fakePlot3.SetFillStyle(3001)
   fakePlot3.SetLineColor(6)
   fakePlot3.SetLineWidth(3)
   if order == 'NLO': legend.AddEntry(fakePlot3, "NLO Theoretical prediction", "l")
   else: legend.AddEntry(fakePlot3, "Theoretical prediction", "l")

##### text
pt = ROOT.TPaveText(0.1663218-0.02,0.886316,0.3045977-0.02,0.978947,"brNDC")
pt.SetBorderSize(0)
pt.SetTextAlign(12)
pt.SetTextFont(62)
pt.SetTextSize(0.05)
pt.SetFillColor(0)
pt.SetFillStyle(0)
pt.AddText("CMS #font[52]{Preliminary}")

pt2 = ROOT.TPaveText(0.70,0.9066667,0.8997773,0.957037,"brNDC")
pt2.SetBorderSize(0)
pt2.SetFillColor(0)
pt2.SetTextSize(0.040)
pt2.SetTextFont(42)
pt2.SetFillStyle(0)
pt2.AddText("          138 fb^{-1} (13 TeV)")

pt4 = ROOT.TPaveText(0.6819196+0.036,0.7180357+0.015+0.02-0.05,0.9008929+0.036,0.8075595+0.015,"brNDC")
pt4.SetTextAlign(12)
pt4.SetFillColor(ROOT.kWhite)
pt4.SetFillStyle(1001)
pt4.SetTextFont(42)
pt4.SetTextSize(0.05)
pt4.SetBorderSize(0)
pt4.SetTextAlign(32)
pt4.AddText("")
pt4.AddText("m_{a} = %s GeV"%mllp)
pt4.AddText("")
pt4.AddText("c#tau_{a}= %.3f m"%(float(ctau)/1000) )  

pt5 = ROOT.TPaveText(0.4819196+0.036,0.7780357+0.015+0.02,0.9008929+0.036,0.8675595+0.015,"brNDC")
pt5.SetTextAlign(12)
pt5.SetFillColor(ROOT.kWhite)
pt5.SetFillStyle(1001)
pt5.SetTextFont(42)
pt5.SetTextSize(0.05)
pt5.SetBorderSize(0)
pt5.SetTextAlign(32)
pt5.AddText("CSC+DT Combination")

th = ROOT.TGraph( n, x, y )
th.SetFillColor(6)
th.SetFillStyle(3001)
th.SetLineColor(6)
th.SetLineWidth(3)


xrg=300
yrg=1000
if mllp=='2':
    xrg=200
    yrg=800

hframe = ROOT.TH1F('hframe', '', 100, xrg, yrg)
hframe.SetMinimum(0.0001)
hframe.SetMaximum(10)
hframe.GetYaxis().SetTitleSize(0.047)
hframe.GetXaxis().SetTitleSize(0.055)
hframe.GetYaxis().SetLabelSize(0.045)
hframe.GetXaxis().SetLabelSize(0.045)
hframe.GetXaxis().SetLabelOffset(0.012)
hframe.GetYaxis().SetTitleOffset(1.4)
hframe.GetXaxis().SetTitleOffset(1.1)
hframe.GetYaxis().SetNdivisions(505)
hframe.GetYaxis().SetTitle("#sigma [pb]")
hframe.GetXaxis().SetTitle("m_{VLL} [GeV]")

hframe.SetStats(0)
ROOT.gPad.SetTicky()
ROOT.gPad.SetLogy()
hframe.Draw()
if categ==True:
  grexp.Draw("L same")
  grexp_csc.Draw("L same")
  grexp_dt.Draw("L same")
  if unblind==True:
    grobs_csc.Draw("L same")
    grobs_dt.Draw("L same")
    grobs.Draw("L same")
  th.Draw( 'l same' )
  pt.Draw()
  pt2.Draw()
  pt4.Draw()
else:
  gr2sigma.Draw("3same")
  gr1sigma.Draw("3same")
  grexp.Draw("Lsame")
  th.Draw( 'l same' )
  if unblind==True: grobs.Draw("Lsame")
  pt.Draw()
  pt2.Draw()
  pt4.Draw()
  pt5.Draw()
redrawBorder()
c1.Update()
legend.Draw()
c1.Update()
if categ==True:
   c1.SaveAs("plots_%s/vlllimits_vs_mvll/vlllimits_vs_mvll_%s_categ.pdf"%(version,ctau)  )
else:
   c1.SaveAs("plots_%s/vlllimits_vs_mvll/vlllimits_vs_mvll_%s.pdf"%(version,ctau) )
