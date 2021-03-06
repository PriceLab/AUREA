from pyBabel.Client import Client
from pyBabel.Extensions import ext
from parser.SOFTParser import SOFTParser
import re
"""
sp = SOFTParser('data/GDS3289.soft.gz')
#sp.printTable()
#exit()
sp2 = SOFTParser('data/GDS2545.soft.gz')
ref = sp.getID_REF()
#print ref
ref2 = sp2.getID_REF()
"""
c = Client()
protein_names = """TENA_HUMAN
ENOA_HUMAN
IRAK3_HUMAN
FINC_HUMAN
LCB2_HUMAN
MKL2_HUMAN
ALDOA_HUMAN
VIME_HUMAN
SORC3_HUMAN
LDHA_HUMAN
PAI1_HUMAN
ENOG_HUMAN
TFPI2_HUMAN
ACTB_HUMAN
TPIS_HUMAN
ALBU_HUMAN
LDHB_HUMAN
COF1_HUMAN
KPYM_HUMAN
ACTH_HUMAN
HS90B_HUMAN
TIMP1_HUMAN
EGFR_HUMAN
CO6A3_HUMAN
1433G_HUMAN
DESM_HUMAN
PGK1_HUMAN
1433T_HUMAN
EF2_HUMAN
G3P_HUMAN
CO3_HUMAN
HS90A_HUMAN
RB3GP_HUMAN
PAI2_HUMAN
TITIN_HUMAN
EF1A1_HUMAN
PROF1_HUMAN
K2C1_HUMAN
1433E_HUMAN
ATG4B_HUMAN
UBIQ_HUMAN
1433Z_HUMAN
PCLO_HUMAN
H4_HUMAN
ANXA1_HUMAN
PGAM1_HUMAN
VINC_HUMAN
PPIA_HUMAN
THIO_HUMAN
FETUA_HUMAN
NDKA_HUMAN
NDKB_HUMAN
ANXA2_HUMAN
HSP7C_HUMAN
TKT_HUMAN
GSTO1_HUMAN
ITB1_HUMAN
S10A6_HUMAN
LEPR_HUMAN
PRDX1_HUMAN
LATS2_HUMAN
FLNA_HUMAN
LEG1_HUMAN
ACTN4_HUMAN
NAMPT_HUMAN
K1718_HUMAN
ALDR_HUMAN
TERA_HUMAN
UCHL1_HUMAN
ITA3_HUMAN
MMP3_HUMAN
MOES_HUMAN
CYTB_HUMAN
STC1_HUMAN
I20RA_HUMAN
PEBP1_HUMAN
CG024_HUMAN
BGH3_HUMAN
LG3BP_HUMAN
S10AB_HUMAN
CLUS_HUMAN
CO6A2_HUMAN
GDIB_HUMAN
LUZP1_HUMAN
CLAT_HUMAN
CSF3_HUMAN
WDR23_HUMAN
CO6A1_HUMAN
SDC4_HUMAN
DUS13_HUMAN
IL8_HUMAN
FLNC_HUMAN
B2MG_HUMAN
MMP2_HUMAN
PMIP_HUMAN
CDC6_HUMAN
ALDOC_HUMAN
TAGL2_HUMAN
TLN1_HUMAN
MPRI_HUMAN
CALU_HUMAN
SAP_HUMAN
IPYR2_HUMAN
IMB1_HUMAN
K1C10_HUMAN
RT31_HUMAN
G6PI_HUMAN
NGAP_HUMAN
SCYL2_HUMAN
PSB5_HUMAN
SH3L3_HUMAN
TCTP_HUMAN
H2A1H_HUMAN
PRDX2_HUMAN
MIF_HUMAN
PARP9_HUMAN
TIM_HUMAN
LRRK2_HUMAN
ANXA6_HUMAN
NFX1_HUMAN
PRDX6_HUMAN
UB2V1_HUMAN
PPIB_HUMAN
H31T_HUMAN
CH10_HUMAN
GSTP1_HUMAN
MMP1_HUMAN
TBA6_HUMAN
RAB1B_HUMAN
OTOF_HUMAN
FMO3_HUMAN
EF1G_HUMAN
MS4A7_HUMAN
ROA1_HUMAN
CYC_HUMAN
PDIA1_HUMAN
GDIR_HUMAN
ANXA5_HUMAN
TXNL5_HUMAN
CALR_HUMAN
CLIC1_HUMAN
CBPA4_HUMAN
PARK7_HUMAN
VPS16_HUMAN
TEAD1_HUMAN
MTPN_HUMAN
MDHC_HUMAN
CSPG2_HUMAN
RFC5_HUMAN
HMCS1_HUMAN
CK016_HUMAN
PSB1_HUMAN
GEMI7_HUMAN
RON_HUMAN
CLIC4_HUMAN
FLNB_HUMAN
LRP4_HUMAN
RLA0_HUMAN
TPM4_HUMAN
CU013_HUMAN
AATM_HUMAN
CUL1_HUMAN
CLAP2_HUMAN
CK046_HUMAN
H2B1C_HUMAN
SYGP1_HUMAN
IF5A1_HUMAN
QSCN6_HUMAN
ABCB6_HUMAN
SF3B1_HUMAN
NRP1_HUMAN
MACF1_HUMAN
GDF9_HUMAN
STC2_HUMAN
RUXE_HUMAN
COQ4_HUMAN
CLH1_HUMAN
TPC6B_HUMAN
DOPD_HUMAN
RAN_HUMAN
DDEF2_HUMAN
AT11C_HUMAN
LGI2_HUMAN
DPOLN_HUMAN
CD44_HUMAN
GNRP_HUMAN
IMB3_HUMAN
PSB3_HUMAN
UB2L3_HUMAN
CAP1_HUMAN
CCD19_HUMAN
VEZA_HUMAN
ZN273_HUMAN
CD9_HUMAN
TALDO_HUMAN
SPAT4_HUMAN
PTX3_HUMAN
SSRP1_HUMAN
RAB7_HUMAN
PCDA5_HUMAN
TIMP2_HUMAN
PDIA3_HUMAN
CDC27_HUMAN
GDF15_HUMAN
T2FA_HUMAN
DLGP1_HUMAN
NPM_HUMAN
DET1_HUMAN
POPD2_HUMAN
CS010_HUMAN
RS28_HUMAN
COTL1_HUMAN
IL6_HUMAN
PSA7_HUMAN
HMGA1_HUMAN
CP2J2_HUMAN
MY18B_HUMAN
GCP2_HUMAN
SET_HUMAN
ABCA2_HUMAN
RS4X_HUMAN
CSF1_HUMAN
ITA5_HUMAN
OAS2_HUMAN
RLA1_HUMAN
AHSA1_HUMAN
UFM1_HUMAN
TBB2_HUMAN
DDX21_HUMAN
AK1C3_HUMAN
ABCA5_HUMAN
EPCR_HUMAN
DLC2A_HUMAN
LPHN3_HUMAN
K1C9_HUMAN
ROA2_HUMAN
C1QBP_HUMAN
BCLF1_HUMAN
STB5L_HUMAN
CH60_HUMAN
IF4A1_HUMAN
ITIH4_HUMAN
CUTA_HUMAN
PA2GE_HUMAN
CAB45_HUMAN
ARPC4_HUMAN
NEO1_HUMAN
ADX_HUMAN
IKAP_HUMAN
CBPA5_HUMAN
ZN644_HUMAN
IF34_HUMAN
HPRT_HUMAN
ITIH2_HUMAN
RAB3I_HUMAN
DOCK7_HUMAN
FA29A_HUMAN
PTD4_HUMAN
TRI17_HUMAN
TULP4_HUMAN
TXNL2_HUMAN
H2BFM_HUMAN
GBB1_HUMAN
SODC_HUMAN
PSA6_HUMAN
RBM28_HUMAN
IBP6_HUMAN
COPD_HUMAN
RS16_HUMAN
GBG12_HUMAN
CD81_HUMAN
PSA4_HUMAN
RBBP8_HUMAN
IFIT3_HUMAN
COPG_HUMAN
TPX2_HUMAN
FCN2_HUMAN
EMAL4_HUMAN
LMNA_HUMAN
MGN_HUMAN
CNTP3_HUMAN
MA2A1_HUMAN
ORC4_HUMAN
TEX2_HUMAN
LRC59_HUMAN
NPC2_HUMAN
ARP3_HUMAN
SMD3_HUMAN
ARMET_HUMAN
CYTC_HUMAN
HNRPQ_HUMAN
Z3H7B_HUMAN
RDH11_HUMAN
LIN1_HUMAN
ILF2_HUMAN
PSA1_HUMAN
BASP_HUMAN
SPTA2_HUMAN
MDHM_HUMAN
EFHD1_HUMAN
RED_HUMAN
AATC_HUMAN
ROAA_HUMAN
MK1I1_HUMAN
WAPL_HUMAN
TFPI1_HUMAN
ZBT20_HUMAN
PDIA6_HUMAN
GNPI_HUMAN
BMX_HUMAN
RM03_HUMAN
RAC1_HUMAN
ARFP1_HUMAN
RHOA_HUMAN
PHS_HUMAN
NP1L1_HUMAN
TF3C5_HUMAN
OPHN1_HUMAN
CRBS_HUMAN
FRIH_HUMAN
AT1A3_HUMAN
LTB1S_HUMAN
SDS3_HUMAN
HEM3_HUMAN
LAMC1_HUMAN
PGM1_HUMAN
FKB1A_HUMAN
A4_HUMAN
ITAV_HUMAN
IMA4_HUMAN
NOLC1_HUMAN
6PGL_HUMAN
PIGV_HUMAN
IRF7_HUMAN
CHD6_HUMAN
UFO_HUMAN
FAM3C_HUMAN
PSA3_HUMAN
VEGFA_HUMAN
TICN1_HUMAN
6PGD_HUMAN
ADH4_HUMAN
PRR12_HUMAN
ZN435_HUMAN
MOL1A_HUMAN
CAND1_HUMAN
CD45_HUMAN
STX3_HUMAN
ZN595_HUMAN"""
pn = [x.strip() for x in protein_names.split('\n')]
"""
for a in c.getIDTypes().keys():
    if len( c.translate(input_type=a, output_types=[a], input_ids=pn)) > 0:
        print a
"""

input = 'protein_uniprot_symbol'
#input = 'gene_entrez'
z = c.translate(input_type=input, output_types=[input], input_ids=pn)
y = [x[0] for x in z]
unmatched = []
for a in pn:
    if a not in y:
        unmatched.append(a)

print len(unmatched)
pn = [a[:-6] for a in unmatched]
for a in c.getIDTypes().keys():
    if a != 'chip_affy':
        if len( c.translate(input_type=a, output_types=[a], input_ids=pn)) > 0:
            print a
a= 'gene_symbol_synonym'
print c.translate(input_type=a, output_types=[input], input_ids=pn)
"""
print pbext.discoverID(ref, pbext.get, numIDs=1000)
print pbext.mergeProbes(ref, ref2)
print pbext.getControls(ref)
#print c.translateAll(input_type='probe_nu',output_types=output)
"""
