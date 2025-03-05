from enum import Enum

class SummaryDomain(Enum):
    BEAUTY: str = "beauty"
    DENTAL: str = "dental"
    MENTAL: str = "mental"
    
    def __eq__(self, other):
        return self.value == other
       