"""Q-IMMUNE QDS - Statistical Threat Detection Engine (Zero AI/ML)."""

from .calibration import BaselineCalibrator, CalibrationProfile, DEFAULT_CALIBRATION
from .qber import ErrorRateCalculator, ErrorMetrics
from .chi_square import StatisticalHypothesisEngine, StatisticalTestResult
from .sprt import WaldSPRT, SPRTResult, SPRTDecision
from .entropy import EntropyDiagnostics
from .finite_sample import FiniteSampleBounds
from .thresholds import CalibratedThresholdEngine

__all__ = [
    "BaselineCalibrator",
    "CalibrationProfile",
    "DEFAULT_CALIBRATION",
    "ErrorRateCalculator",
    "ErrorMetrics",
    "StatisticalHypothesisEngine",
    "StatisticalTestResult",
    "WaldSPRT",
    "SPRTResult",
    "SPRTDecision",
    "EntropyDiagnostics",
    "FiniteSampleBounds",
    "CalibratedThresholdEngine",
]
