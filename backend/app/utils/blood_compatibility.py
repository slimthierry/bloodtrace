"""Blood compatibility matrix implementing ABO+Rh system rules.

This module contains the core blood compatibility logic used throughout
the blood bank module for safe transfusion matching.

ABO Blood Group System:
- Type A has A antigens, anti-B antibodies
- Type B has B antigens, anti-A antibodies
- Type AB has A and B antigens, no antibodies (universal recipient for RBC)
- Type O has no antigens, anti-A and anti-B antibodies (universal donor for RBC)

Rh Factor:
- Rh+ has D antigen
- Rh- lacks D antigen
- Rh- blood can be given to Rh+ recipients
- Rh+ blood should NOT be given to Rh- recipients
"""

from typing import List, Tuple


# RBC (Red Blood Cell) compatibility matrix
# Key: recipient type, Value: list of compatible donor types
RBC_COMPATIBILITY = {
    "O-":  ["O-"],
    "O+":  ["O-", "O+"],
    "A-":  ["O-", "A-"],
    "A+":  ["O-", "O+", "A-", "A+"],
    "B-":  ["O-", "B-"],
    "B+":  ["O-", "O+", "B-", "B+"],
    "AB-": ["O-", "A-", "B-", "AB-"],
    "AB+": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],  # Universal recipient
}

# Plasma compatibility matrix (inverted from RBC)
# Key: recipient type, Value: list of compatible donor types
PLASMA_COMPATIBILITY = {
    "O-":  ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],  # Universal recipient for plasma
    "O+":  ["O+", "A+", "B+", "AB+"],
    "A-":  ["A-", "A+", "AB-", "AB+"],
    "A+":  ["A+", "AB+"],
    "B-":  ["B-", "B+", "AB-", "AB+"],
    "B+":  ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"],  # Universal donor for plasma
}

# All 8 blood groups
ALL_BLOOD_GROUPS = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]


def _to_group(blood_type: str, rh_factor: str) -> str:
    """Combine blood type and Rh factor into a blood group string."""
    return f"{blood_type}{rh_factor}"


def is_rbc_compatible(
    donor_blood_type: str,
    donor_rh: str,
    recipient_blood_type: str,
    recipient_rh: str,
) -> bool:
    """Check if donor RBC blood is compatible with recipient.

    Args:
        donor_blood_type: Donor ABO type (A, B, AB, O)
        donor_rh: Donor Rh factor (+, -)
        recipient_blood_type: Recipient ABO type (A, B, AB, O)
        recipient_rh: Recipient Rh factor (+, -)

    Returns:
        True if the donor can give RBC to the recipient.
    """
    donor_group = _to_group(donor_blood_type, donor_rh)
    recipient_group = _to_group(recipient_blood_type, recipient_rh)

    compatible_donors = RBC_COMPATIBILITY.get(recipient_group, [])
    return donor_group in compatible_donors


def is_plasma_compatible(
    donor_blood_type: str,
    donor_rh: str,
    recipient_blood_type: str,
    recipient_rh: str,
) -> bool:
    """Check if donor plasma is compatible with recipient.

    For plasma, compatibility rules are inverted from RBC:
    - AB is universal plasma donor
    - O is universal plasma recipient

    Args:
        donor_blood_type: Donor ABO type (A, B, AB, O)
        donor_rh: Donor Rh factor (+, -)
        recipient_blood_type: Recipient ABO type (A, B, AB, O)
        recipient_rh: Recipient Rh factor (+, -)

    Returns:
        True if the donor can give plasma to the recipient.
    """
    donor_group = _to_group(donor_blood_type, donor_rh)
    recipient_group = _to_group(recipient_blood_type, recipient_rh)

    compatible_donors = PLASMA_COMPATIBILITY.get(recipient_group, [])
    return donor_group in compatible_donors


def get_compatible_donor_types(
    recipient_blood_type: str,
    recipient_rh: str,
    component: str = "packed_rbc",
) -> List[Tuple[str, str]]:
    """Get list of compatible donor blood types for a recipient.

    Args:
        recipient_blood_type: Recipient ABO type
        recipient_rh: Recipient Rh factor
        component: Blood component type

    Returns:
        List of (blood_type, rh_factor) tuples that are compatible.
    """
    recipient_group = _to_group(recipient_blood_type, recipient_rh)

    if component in ("plasma", "cryoprecipitate"):
        compatible_groups = PLASMA_COMPATIBILITY.get(recipient_group, [])
    else:
        compatible_groups = RBC_COMPATIBILITY.get(recipient_group, [])

    result = []
    for group in compatible_groups:
        if group.startswith("AB"):
            result.append(("AB", group[2:]))
        else:
            result.append((group[0], group[1:]))

    return result


def get_full_compatibility_matrix() -> dict:
    """Get the complete compatibility matrix for display in the UI.

    Returns:
        Dictionary with 'rbc' and 'plasma' matrices, each being a dict
        mapping recipient groups to lists of compatible donor groups.
    """
    return {
        "rbc": {
            recipient: {
                "compatible_donors": donors,
                "is_universal_recipient": recipient == "AB+",
                "is_universal_donor": recipient == "O-",
            }
            for recipient, donors in RBC_COMPATIBILITY.items()
        },
        "plasma": {
            recipient: {
                "compatible_donors": donors,
                "is_universal_recipient": recipient == "O-",
                "is_universal_donor": recipient == "AB+",
            }
            for recipient, donors in PLASMA_COMPATIBILITY.items()
        },
        "blood_groups": ALL_BLOOD_GROUPS,
    }
