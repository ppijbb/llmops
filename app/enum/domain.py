from enum import Enum

class SummaryDomain(Enum):
    BEAUTY: str = "beauty"
    DENTAL: str = "dental"
    MENTAL: str = "mental"
    TEST: str = "den_llm_test"
    
    def __eq__(self, other):
        return self.value == other
       