"""The project's clean, machine-readable development metalanguage.

These names carry private symbolic meaning while remaining ordinary enums that
are useful to the software. Operational decisions must still follow telemetry.
"""

from enum import IntEnum, StrEnum


class DevelopmentStage(IntEnum):
    VOID = 0
    SEED = 1
    FORM = 2
    TRIAL = 3
    CURRENT = 4
    YIELD = 5
    MULTIPLICATION = 6
    SEA = 7


class ValueState(StrEnum):
    DORMANT = "DORMANT"
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    VERIFIED = "VERIFIED"
    PAYABLE = "PAYABLE"
    FUNDED = "FUNDED"
    SETTLED = "SETTLED"
    BANKED = "BANKED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    DISPUTED = "DISPUTED"

