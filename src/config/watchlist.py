from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class WatchItem:
    ticker: str
    name: str
    subsector: str
    region: str

WATCHLIST: List[WatchItem] = [
    # Major Global Renewable Energy Companies
    WatchItem('NEE',  'NextEra Energy, Inc.', 'Utility', 'US'),
    WatchItem('IBDRY','Iberdrola SA ADR', 'Utility', 'EU'),
    WatchItem('GEV',  'GE Vernova Inc.', 'Energy Equipment', 'US'),
    WatchItem('VWDRY','Vestas Wind Systems A/S', 'Wind', 'EU'),
    WatchItem('BEPC', 'Brookfield Renewable Corporation', 'Utility', 'US'),
    WatchItem('JKS',  'JinkoSolar Holding Co., Ltd.', 'Solar', 'Asia'),
    WatchItem('ENPH', 'Enphase Energy, Inc.', 'Solar', 'US'),
    WatchItem('FSLR', 'First Solar, Inc.', 'Solar', 'US'),
    
    # Solar Energy Companies
    WatchItem('CSIQ', 'Canadian Solar Inc.', 'Solar', 'US'),
    WatchItem('RUN',  'Sunrun Inc.', 'Solar', 'US'),
    WatchItem('SEDG', 'SolarEdge Technologies, Inc.', 'Solar', 'US'),
    WatchItem('ARRY', 'Array Technologies, Inc.', 'Solar', 'US'),
    
    # Wind Energy Companies
    WatchItem('DNNGY','Ørsted A/S', 'Wind', 'EU'),
    WatchItem('SIEGY','Siemens Energy AG', 'Wind', 'EU'),
    WatchItem('TPIC', 'TPI Composites, Inc.', 'Wind', 'US'),
    
    # Hydrogen and Fuel Cells
    WatchItem('PLUG', 'Plug Power Inc.', 'Hydrogen', 'US'),
    WatchItem('BE',   'Bloom Energy Corporation', 'Hydrogen', 'US'),
    WatchItem('BLDP', 'Ballard Power Systems Inc.', 'Hydrogen', 'US'),
    
    # Diversified and Other Renewables
    WatchItem('CWEN', 'Clearway Energy, Inc.', 'Utility', 'US'),
    WatchItem('PWR',  'Quanta Services, Inc.', 'Energy Equipment', 'US'),
    WatchItem('AMRC', 'Ameresco, Inc.', 'Energy Services', 'US'),
    WatchItem('ORA',  'Ormat Technologies, Inc.', 'Geothermal', 'US'),
]
