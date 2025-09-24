from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class WatchItem:
    ticker: str
    name: str
    subsector: str
    region: str

WATCHLIST: List[WatchItem] = [
    WatchItem('FSLR', 'First Solar, Inc.', 'Solar', 'US'),
    WatchItem('ENPH', 'Enphase Energy, Inc.', 'Solar', 'US'),
    WatchItem('RUN',  'Sunrun Inc.', 'Solar', 'US'),
    WatchItem('NEE',  'NextEra Energy, Inc.', 'Utility', 'US'),
    WatchItem('BEPC', 'Brookfield Renewable Corporation', 'Utility', 'US'),
    WatchItem('VWDRY','Vestas Wind Systems A/S', 'Wind', 'EU'),
    WatchItem('DNNGY','Ørsted A/S', 'Wind', 'EU'),
]
