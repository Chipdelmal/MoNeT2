#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from glob import glob
import STP_aux as aux
import STP_gene as drv
import STP_land as lnd
import STP_functions as fun
from datetime import datetime
import MoNeT_MGDrivE as monet
import compress_pickle as pkl


(USR, AOI, REL, LND, MGV) = (sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
# (USR, AOI, REL, LND, MGV) = ('srv', 'HUM', 'male', 'EPI', 'v2')
# (USR, AOI, REL, LND, MGV) = ('dsk', 'HLT', 'male', 'EPI', 'v2')
# (USR, AOI, REL, LND, MGV) = ('dsk', 'HLT', '106', 'SPA', 'v1')
(DRV, FMT, OVW, FZ) = ('LDR', 'bz2', True, False)
tStable = 90
###############################################################################
# Setting up paths and style
###############################################################################
# Paths -----------------------------------------------------------------------
(PT_ROT, PT_IMG, PT_DTA, PT_PRE, PT_OUT, PT_MTR) = aux.selectPath(USR, LND, REL)
PT_IMG = PT_IMG + 'preTraces/'
monet.makeFolder(PT_IMG)
# Drive and land --------------------------------------------------------------
if LND == 'SPA':
    pop = 10000
else:
    pop = 100000
(DRV, MGV) = aux.humanSelector(AOI, DRV, MGV)
(drive, land) = (
    drv.driveSelector(DRV, AOI, popSize=pop), 
    lnd.landSelector(LND, REL, PT_ROT)
)
(CLR, YRAN) = (drive.get('colors'), drive.get('yRange'))
STYLE = {
    "width": .5, "alpha": .6, "dpi": 200, "legend": True, "aspect": .25,
    "colors": CLR, "xRange": [0, 365 * 6], "yRange": [0, YRAN]
}
STYLE['aspect'] = monet.scaleAspect(1, STYLE)
# Setup the run ---------------------------------------------------------------
tS = datetime.now()
monet.printExperimentHead(PT_ROT, PT_IMG, tS, 'UCIMI PreTraces '+AOI)
###############################################################################
# Load preprocessed files lists
###############################################################################
tyTag = ('sum', 'srp')
(fltrPattern, globPattern) = ('dummy', PT_PRE+'*'+AOI+'*'+'{}'+'*')
if FZ:
    fltrPattern = PT_PRE+'*_00_*'+AOI+'*'+'{}'+'*'
fLists = monet.getFilteredTupledFiles(fltrPattern, globPattern, tyTag)
###############################################################################
# Process files
###############################################################################
(xpNum, digs) = monet.lenAndDigits(fLists)
for i in range(0, xpNum):
    monet.printProgress(i+1, xpNum, digs)
    (sumDta, repDta) = [pkl.load(file) for file in (fLists[i])]
    name = fLists[i][0].split('/')[-1].split('.')[0][:-4]
    # Traces ------------------------------------------------------------------
    balPop = sum(sumDta['population'][tStable])
    STYLE['yRange'] = (0,  balPop/2+balPop*.2)
    if AOI == 'ECO':
        STYLE['yRange'] = (STYLE['yRange'][0], STYLE['yRange'][1]*2)
    STYLE['aspect'] = monet.scaleAspect(1, STYLE)
    monet.exportTracesPlot(
        repDta, name, STYLE, PT_IMG, vLines=[0, 0], wopPrint=False, wop=i
    )
###############################################################################
# Export plot legend
###############################################################################
if len(fLists) > 0:
    cl = [i[:-2]+'cc' for i in CLR]
    monet.exportGeneLegend(
        sumDta['genotypes'], cl, PT_IMG+'/plt_{}.png'.format(AOI), 500
    )
