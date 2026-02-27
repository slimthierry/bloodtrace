"""Validation utilities for BloodTrace data."""

import re
from datetime import date
from typing import Optional


VALID_BLOOD_TYPES = {"A", "B", "AB", "O"}
VALID_RH_FACTORS = {"+", "-"}
VALID_COMPONENTS = {
    "whole_blood",
    "packed_rbc",
    "plasma",
    "platelets",
    "cryoprecipitate",
}
VALID_URGENCIES = {"routine", "urgent", "emergency", "massive"}
VALID_BAG_STATUSES = {
    "available",
    "reserved",
    "crossmatched",
    "transfused",
    "expired",
    "discarded",
    "quarantine",
}
VALID_SCREENING_STATUSES = {"pending", "passed", "failed"}
VALID_ELIGIBILITY_STATUSES = {"eligible", "temporary_deferral", "permanent_deferral"}
VALID_REACTION_TYPES = {"none", "mild", "moderate", "severe"}
VALID_REQUEST_STATUSES = {"pending", "approved", "in_progress", "completed", "cancelled"}


def validate_blood_type(blood_type: str) -> bool:
    """Validate ABO blood type."""
    return blood_type in VALID_BLOOD_TYPES


def validate_rh_factor(rh_factor: str) -> bool:
    """Validate Rh factor."""
    return rh_factor in VALID_RH_FACTORS


def validate_blood_group(blood_group: str) -> bool:
    """Validate a combined blood group string (e.g., 'AB+', 'O-')."""
    if len(blood_group) < 2:
        return False
    rh = blood_group[-1]
    bt = blood_group[:-1]
    return validate_blood_type(bt) and validate_rh_factor(rh)


def validate_component(component: str) -> bool:
    """Validate blood component type."""
    return component in VALID_COMPONENTS


def validate_ipp(ipp: str) -> bool:
    """Validate IPP (Identifiant Permanent du Patient) format.

    IPP should be alphanumeric, between 3 and 50 characters.
    """
    if not ipp or len(ipp) < 3 or len(ipp) > 50:
        return False
    return bool(re.match(r"^[A-Za-z0-9\-]+$", ipp))


def validate_volume(volume_ml: int) -> bool:
    """Validate donation/bag volume in milliliters."""
    return 50 <= volume_ml <= 1000


def validate_donation_eligibility(
    last_donation_date: Optional[date],
    min_days_between: int = 56,
) -> tuple[bool, Optional[str]]:
    """Check if enough time has passed since last donation.

    Standard minimum interval is 56 days (8 weeks) between whole blood donations.
    """
    if last_donation_date is None:
        return True, None

    days_since = (date.today() - last_donation_date).days
    if days_since < min_days_between:
        remaining = min_days_between - days_since
        return False, (
            f"Delai minimum non respecte: {days_since} jours depuis le dernier don. "
            f"Il reste {remaining} jours avant eligibilite."
        )

    return True, None
