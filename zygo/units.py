# -*- coding: utf-8 -*-

# ****************************************************************************
# THIS PROGRAM IS AN UNPUBLISHED WORK FULLY PROTECTED BY THE UNITED
# STATES COPYRIGHT LAWS AND IS CONSIDERED A TRADE SECRET BELONGING TO
# THE COPYRIGHT HOLDER. IT IS COVERED BY THE ZYGO SOFTWARE LICENSE AGREEMENT.
# COPYRIGHT (c) ZYGO CORPORATION.
#
# ****************************************************************************

"""
Provides support for Mx units
"""

from enum import Enum


def _validate_unit(unit):
    """Validate input as a valid units value.

    Parameters
    ----------
    unit : Units or str
        Unit to validate.

    Returns
    -------
    str
        String representation of the specified unit.

    Raises
    ------
    TypeError
        If the input is not a Units or str type.
    ValueError
        If the input string is not convertable to a Units member.
    """
    if unit is None:
        unit = Units.NoUnits
    if isinstance(unit, Units):
        return unit.name
    if isinstance(unit, str):
        for ustr in Units.__members__:
            if unit.lower() == ustr.lower():
                return ustr
        raise ValueError('`unit` string is not a valid `Units` member.')
    raise TypeError('`unit` must be of type `Units` or a valid string value.')


class _AutoNumber(Enum):
    """Helper class to allow creating enum values without explicit
    numbering.
    """
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class Units(_AutoNumber):
    """Enumeration of Mx-supported units."""
    # These units come directly from the Mx Unit class.
    # The enum is provided as a convenience for the scripting end-user.
    # Order does not matter, since the units are converted to their string
    # representation prior to serialization.
    Invalid = ()
    NotSet = ()
    NoUnits = ()

    # Linear
    Angstroms = ()
    CentiMeters = ()
    Feet = ()
    Inches = ()
    Meters = ()
    MicroInches = ()
    MicroMeters = ()
    Mils = ()
    MilliMeters = ()
    NanoInches = ()
    NanoMeters = ()
    DmiModeF1 = ()
    DmiModeF2 = ()

    # Nonphysical Height
    Waves = ()
    UserWaves = ()
    FringeRadians = ()
    Fringes = ()

    # Nonphysical Lateral
    Pixels = ()

    Scaled = ()

    # Angles
    ArcMinutes = ()
    ArcSeconds = ()
    Degrees = ()
    MicroRadians = ()
    MilliRadians = ()
    Radians = ()
    MilliDegrees = ()

    # Area
    SquareAngstroms = ()
    SquareCentiMeters = ()
    SquareFeet = ()
    SquareInches = ()
    SquareMeters = ()
    SquareMicroInches = ()
    SquareMicroMeters = ()
    SquareMilliMeters = ()
    SquareMils = ()
    SquareNanoInches = ()
    SquareNanoMeters = ()

    # Nonphysical Area
    SquarePixels = ()

    # Volume
    CubicAngstroms = ()
    CubicCentiMeters = ()
    CubicFeet = ()
    CubicInches = ()
    CubicMeters = ()
    CubicMicroInches = ()
    CubicMicroMeters = ()
    CubicMilliMeters = ()
    CubicNanoInches = ()
    CubicNanoMeters = ()
    CubicMils = ()

    # Temp
    Kelvin = ()
    Celsius = ()
    Fahrenheit = ()

    # Spatial Frequency
    CycPerAngstrom = ()
    CycPerCentiMeter = ()
    CycPerFoot = ()
    CycPerInch = ()
    CycPerMeter = ()
    CycPerMicroInch = ()
    CycPerMicroMeter = ()
    CycPerMil = ()
    CycPerMilliMeter = ()
    CycPerNanoInch = ()
    CycPerNanoMeter = ()

    # Nonphysical Lateral Spatial Frequency
    CycPerPixel = ()

    # Velocity = ()
    MetersPerHour = ()
    MetersPerMinute = ()
    MetersPerSecond = ()
    MetersPerMilliSecond = ()
    MetersPerMicroSecond = ()
    CentiMetersPerHour = ()
    CentiMetersPerMinute = ()
    CentiMetersPerSecond = ()
    CentiMetersPerMilliSecond = ()
    CentiMetersPerMicroSecond = ()
    MilliMetersPerHour = ()
    MilliMetersPerMinute = ()
    MilliMetersPerSecond = ()
    MilliMetersPerMilliSecond = ()
    MilliMetersPerMicroSecond = ()
    MicroMetersPerHour = ()
    MicroMetersPerMinute = ()
    MicroMetersPerSecond = ()
    MicroMetersPerMilliSecond = ()
    MicroMetersPerMicroSecond = ()
    NanoMetersPerHour = ()
    NanoMetersPerMinute = ()
    NanoMetersPerSecond = ()
    NanoMetersPerMilliSecond = ()
    NanoMetersPerMicroSecond = ()
    AngstromsPerHour = ()
    AngstromsPerMinute = ()
    AngstromsPerSecond = ()
    AngstromsPerMilliSecond = ()
    AngstromsPerMicroSecond = ()
    FeetPerHour = ()
    FeetPerMinute = ()
    FeetPerSecond = ()
    FeetPerMilliSecond = ()
    FeetPerMicroSecond = ()
    InchesPerHour = ()
    InchesPerMinute = ()
    InchesPerSecond = ()
    InchesPerMilliSecond = ()
    InchesPerMicroSecond = ()
    MilsPerHour = ()
    MilsPerMinute = ()
    MilsPerSecond = ()
    MilsPerMilliSecond = ()
    MilsPerMicroSecond = ()
    MicroInchesPerHour = ()
    MicroInchesPerMinute = ()
    MicroInchesPerSecond = ()
    MicroInchesPerMilliSecond = ()
    MicroInchesPerMicroSecond = ()
    NanoInchesPerHour = ()
    NanoInchesPerMinute = ()
    NanoInchesPerSecond = ()
    NanoInchesPerMilliSecond = ()
    NanoInchesPerMicroSecond = ()

    # Accel = ()
    MetersPerSec2 = ()
    CentiMetersPerSec2 = ()
    MilliMetersPerSec2 = ()
    MicroMetersPerSec2 = ()
    NanoMetersPerSec2 = ()
    AngstromsPerSec2 = ()
    FeetPerSec2 = ()
    InchesPerSec2 = ()
    MilsPerSec2 = ()
    MicroInchesPerSec2 = ()
    NanoInchesPerSec2 = ()

    # Ratio = ()
    RatioUnscaled = ()
    RatioPercent = ()
    RatioPartsPerMillion = ()
    RatioPartsPerBillion = ()

    # Freq = ()
    Hertz = ()
    KiloHertz = ()
    MegaHertz = ()
    GigaHertz = ()
    TeraHertz = ()

    # Time
    MicroSeconds = ()
    MilliSeconds = ()
    Seconds = ()
    Minutes = ()
    Hours = ()
    InvMicroSeconds = ()
    InvMilliSeconds = ()
    InvSeconds = ()
    InvMinutes = ()
    InvHours = ()

    # Camera
    Counts = ()

    # Percent
    Percent = ()

    # Angle Velocity
    RadiansPerHour = ()
    RadiansPerMinute = ()
    RadiansPerSecond = ()
    RadiansPerMilliSecond = ()
    RadiansPerMicroSecond = ()
    MilliRadiansPerHour = ()
    MilliRadiansPerMinute = ()
    MilliRadiansPerSecond = ()
    MilliRadiansPerMilliSecond = ()
    MilliRadiansPerMicroSecond = ()
    MicroRadiansPerHour = ()
    MicroRadiansPerMinute = ()
    MicroRadiansPerSecond = ()
    MicroRadiansPerMilliSecond = ()
    MicroRadiansPerMicroSecond = ()
    DegreesPerHour = ()
    DegreesPerMinute = ()
    DegreesPerSecond = ()
    DegreesPerMilliSecond = ()
    DegreesPerMicroSecond = ()
    MilliDegreesPerHour = ()
    MilliDegreesPerMinute = ()
    MilliDegreesPerSecond = ()
    MilliDegreesPerMilliSecond = ()
    MilliDegreesPerMicroSecond = ()
    ArcMinutesPerHour = ()
    ArcMinutesPerMinute = ()
    ArcMinutesPerSecond = ()
    ArcMinutesPerMilliSecond = ()
    ArcMinutesPerMicroSecond = ()
    ArcSecondsPerHour = ()
    ArcSecondsPerMinute = ()
    ArcSecondsPerSecond = ()
    ArcSecondsPerMilliSecond = ()
    ArcSecondsPerMicroSecond = ()

    # Angle Acceleration
    RadiansPerSec2 = ()
    MilliRadiansPerSec2 = ()
    MicroRadiansPerSec2 = ()
    DegreesPerSec2 = ()
    MilliDegreesPerSec2 = ()
    ArcMinutesPerSec2 = ()
    ArcSecondsPerSec2 = ()

    # Motor
    MotorCounts = ()
    MotorCountsPerSecond = ()
    MotorCountsPerSec2 = ()
    MotorCountsPerSec3 = ()

    # Power Density 1D
    AngstromSquaredMicroMeters = ()
    NanoMeterSquaredMilliMeters = ()
    MicroMeterSquaredMilliMeters = ()
    AngstromsCubed = ()
    NanoMetersCubed = ()
    MicroMetersCubed = ()
    MilliMetersCubed = ()

    # Jerk
    MetersPerSec3 = ()
    CentiMetersPerSec3 = ()
    MilliMetersPerSec3 = ()
    MicroMetersPerSec3 = ()
    NanoMetersPerSec3 = ()
    AngstromsPerSec3 = ()
    FeetPerSec3 = ()
    InchesPerSec3 = ()
    MilsPerSec3 = ()
    MicroInchesPerSec3 = ()
    NanoInchesPerSec3 = ()

    # Angle Jerk
    RadiansPerSec3 = ()
    MilliRadiansPerSec3 = ()
    MicroRadiansPerSec3 = ()
    DegreesPerSec3 = ()
    MilliDegreesPerSec3 = ()
    ArcMinutesPerSec3 = ()
    ArcSecondsPerSec3 = ()

    # Pressure
    Pascal = ()
    Hectopascal = ()
    Kilopascal = ()
    Megapascal = ()
    Bar = ()
    Millibar = ()
    PoundsPerSquareInch = ()
    Torr = ()
    CentimetersMercury = ()
    InchesMercury = ()

    # Energy
    Joules = ()
    ElectronVolts = ()

    # Inverse Energy
    InvJoules = ()
    InvElectronVolts = ()

    # Slope
    MetersPerMeter = ()
    CentiMetersPerMeter = ()
    MilliMetersPerMeter = ()
    MicroMetersPerMeter = ()
    NanoMetersPerMeter = ()
    AngstromsPerMeter = ()
    FeetPerMeter = ()
    InchesPerMeter = ()
    MilsPerMeter = ()
    MicroInchesPerMeter = ()
    NanoInchesPerMeter = ()
    WavesPerMeter = ()
    UserWavesPerMeter = ()
    FringesPerMeter = ()
    FringeRadiansPerMeter = ()
    MetersPerCentiMeter = ()
    CentiMetersPerCentiMeter = ()
    MilliMetersPerCentiMeter = ()
    MicroMetersPerCentiMeter = ()
    NanoMetersPerCentiMeter = ()
    AngstromsPerCentiMeter = ()
    FeetPerCentiMeter = ()
    InchesPerCentiMeter = ()
    MilsPerCentiMeter = ()
    MicroInchesPerCentiMeter = ()
    NanoInchesPerCentiMeter = ()
    WavesPerCentiMeter = ()
    UserWavesPerCentiMeter = ()
    FringesPerCentiMeter = ()
    FringeRadiansPerCentiMeter = ()
    MetersPerMilliMeter = ()
    CentiMetersPerMilliMeter = ()
    MilliMetersPerMilliMeter = ()
    MicroMetersPerMilliMeter = ()
    NanoMetersPerMilliMeter = ()
    AngstromsPerMilliMeter = ()
    FeetPerMilliMeter = ()
    InchesPerMilliMeter = ()
    MilsPerMilliMeter = ()
    MicroInchesPerMilliMeter = ()
    NanoInchesPerMilliMeter = ()
    WavesPerMilliMeter = ()
    UserWavesPerMilliMeter = ()
    FringesPerMilliMeter = ()
    FringeRadiansPerMilliMeter = ()
    MetersPerMicroMeter = ()
    CentiMetersPerMicroMeter = ()
    MilliMetersPerMicroMeter = ()
    MicroMetersPerMicroMeter = ()
    NanoMetersPerMicroMeter = ()
    AngstromsPerMicroMeter = ()
    FeetPerMicroMeter = ()
    InchesPerMicroMeter = ()
    MilsPerMicroMeter = ()
    MicroInchesPerMicroMeter = ()
    NanoInchesPerMicroMeter = ()
    WavesPerMicroMeter = ()
    UserWavesPerMicroMeter = ()
    FringesPerMicroMeter = ()
    FringeRadiansPerMicroMeter = ()
    MetersPerNanoMeter = ()
    CentiMetersPerNanoMeter = ()
    MilliMetersPerNanoMeter = ()
    MicroMetersPerNanoMeter = ()
    NanoMetersPerNanoMeter = ()
    AngstromsPerNanoMeter = ()
    FeetPerNanoMeter = ()
    InchesPerNanoMeter = ()
    MilsPerNanoMeter = ()
    MicroInchesPerNanoMeter = ()
    NanoInchesPerNanoMeter = ()
    WavesPerNanoMeter = ()
    UserWavesPerNanoMeter = ()
    FringesPerNanoMeter = ()
    FringeRadiansPerNanoMeter = ()
    MetersPerAngstrom = ()
    CentiMetersPerAngstrom = ()
    MilliMetersPerAngstrom = ()
    MicroMetersPerAngstrom = ()
    NanoMetersPerAngstrom = ()
    AngstromsPerAngstrom = ()
    FeetPerAngstrom = ()
    InchesPerAngstrom = ()
    MilsPerAngstrom = ()
    MicroInchesPerAngstrom = ()
    NanoInchesPerAngstrom = ()
    WavesPerAngstrom = ()
    UserWavesPerAngstrom = ()
    FringesPerAngstrom = ()
    FringeRadiansPerAngstrom = ()
    MetersPerFoot = ()
    CentiMetersPerFoot = ()
    MilliMetersPerFoot = ()
    MicroMetersPerFoot = ()
    NanoMetersPerFoot = ()
    AngstromsPerFoot = ()
    FeetPerFoot = ()
    InchesPerFoot = ()
    MilsPerFoot = ()
    MicroInchesPerFoot = ()
    NanoInchesPerFoot = ()
    WavesPerFoot = ()
    UserWavesPerFoot = ()
    FringesPerFoot = ()
    FringeRadiansPerFoot = ()
    MetersPerInch = ()
    CentiMetersPerInch = ()
    MilliMetersPerInch = ()
    MicroMetersPerInch = ()
    NanoMetersPerInch = ()
    AngstromsPerInch = ()
    FeetPerInch = ()
    InchesPerInch = ()
    MilsPerInch = ()
    MicroInchesPerInch = ()
    NanoInchesPerInch = ()
    WavesPerInch = ()
    UserWavesPerInch = ()
    FringesPerInch = ()
    FringeRadiansPerInch = ()
    MetersPerMil = ()
    CentiMetersPerMil = ()
    MilliMetersPerMil = ()
    MicroMetersPerMil = ()
    NanoMetersPerMil = ()
    AngstromsPerMil = ()
    FeetPerMil = ()
    InchesPerMil = ()
    MilsPerMil = ()
    MicroInchesPerMil = ()
    NanoInchesPerMil = ()
    WavesPerMil = ()
    UserWavesPerMil = ()
    FringesPerMil = ()
    FringeRadiansPerMil = ()
    MetersPerMicroInch = ()
    CentiMetersPerMicroInch = ()
    MilliMetersPerMicroInch = ()
    MicroMetersPerMicroInch = ()
    NanoMetersPerMicroInch = ()
    AngstromsPerMicroInch = ()
    FeetPerMicroInch = ()
    InchesPerMicroInch = ()
    MilsPerMicroInch = ()
    MicroInchesPerMicroInch = ()
    NanoInchesPerMicroInch = ()
    WavesPerMicroInch = ()
    UserWavesPerMicroInch = ()
    FringesPerMicroInch = ()
    FringeRadiansPerMicroInch = ()
    MetersPerNanoInch = ()
    CentiMetersPerNanoInch = ()
    MilliMetersPerNanoInch = ()
    MicroMetersPerNanoInch = ()
    NanoMetersPerNanoInch = ()
    AngstromsPerNanoInch = ()
    FeetPerNanoInch = ()
    InchesPerNanoInch = ()
    MilsPerNanoInch = ()
    MicroInchesPerNanoInch = ()
    NanoInchesPerNanoInch = ()
    WavesPerNanoInch = ()
    UserWavesPerNanoInch = ()
    FringesPerNanoInch = ()
    FringeRadiansPerNanoInch = ()
    MetersPerPixel = ()
    CentiMetersPerPixel = ()
    MilliMetersPerPixel = ()
    MicroMetersPerPixel = ()
    NanoMetersPerPixel = ()
    AngstromsPerPixel = ()
    FeetPerPixel = ()
    InchesPerPixel = ()
    MilsPerPixel = ()
    MicroInchesPerPixel = ()
    NanoInchesPerPixel = ()
    WavesPerPixel = ()
    UserWavesPerPixel = ()
    FringesPerPixel = ()
    FringeRadiansPerPixel = ()

    # AngularFrequency
    CycPerArcMinute = ()
    CycPerArcSecond = ()
    CycPerDegree = ()
    CycPerMilliDegree = ()
    CycPerRadian = ()
    CycPerMilliRadian = ()
    CycPerMicroRadian = ()

    # PowerDensity2D
    Meters4 = ()
    MilliMeters4 = ()
    MicroMeters4 = ()
    NanoMeters4 = ()

    # AngularPowerDensity
    MicroMeters2PerRadian = ()

    # Inverse Area
    InverseSquareMeters = ()
    InverseSquareCentiMeters = ()
    InverseSquareMilliMeters = ()
    InverseSquareMicroMeters = ()
    InverseSquareNanoMeters = ()
    InverseSquareAngstroms = ()
    InverseSquareFeet = ()
    InverseSquareInches = ()
    InverseSquareMils = ()
    InverseSquareMicroInches = ()
    InverseSquareNanoInches = ()
    InverseSquarePixels = ()
