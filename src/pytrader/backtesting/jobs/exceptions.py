ANALYSIS_NOT_ALLOWED_MESSAGE = """
    the analysis type {} is not allow. Here is what type of analysis you can do {}
    \n 
"""

MACRO_ANALYSIS = [
    "# Trades",
    "Return [%]",
    "Win Rate [%]",
    "Best Trade [%]",
    "Worst Trade [%]",
    "Avg. Trade [%]",
    "Max. Drawdown [%]",
    "Avg. Drawdown [%]",
    "Max. Trade Duration",
    "Avg. Trade Duration",
    "Max. Drawdown Duration",
    "Avg. Drawdown Duration",
]

MICRO_ANALYSIS = ["_trades"]

ALLOWED_ANALYSIS_TYPES = {"MACRO": MACRO_ANALYSIS, "MICRO": MICRO_ANALYSIS}


class AnalysisNotAllowedError(Exception):
    def __init__(self, analysis_type, message=ANALYSIS_NOT_ALLOWED_MESSAGE):
        self.analysis_type = analysis_type
        self.message = message
        super().__init__(
            self.message.format(self.analysis_type, ALLOWED_ANALYSIS_TYPES.keys())
        )
