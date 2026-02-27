"""Blood compatibility service implementing ABO+Rh compatibility rules.

This module implements the complete blood compatibility matrix used for
safe transfusion matching in the blood bank.

Key rules:
- O- is the universal donor for RBC (red blood cells)
- AB+ is the universal recipient for RBC
- For plasma, the rules are inverted: AB is universal donor, O is universal recipient
- Rh- blood can be given to Rh+ recipients, but not vice versa
"""

from app.utils.blood_compatibility import (
    is_rbc_compatible,
    is_plasma_compatible,
    get_compatible_donor_types,
    get_full_compatibility_matrix,
)


def check_compatibility(
    donor_blood_type: str,
    donor_rh: str,
    recipient_blood_type: str,
    recipient_rh: str,
    component: str = "packed_rbc",
) -> dict:
    """Check blood compatibility between donor and recipient.

    Args:
        donor_blood_type: Donor ABO type (A, B, AB, O)
        donor_rh: Donor Rh factor (+, -)
        recipient_blood_type: Recipient ABO type (A, B, AB, O)
        recipient_rh: Recipient Rh factor (+, -)
        component: Blood component type

    Returns:
        Dictionary with compatibility result and details.
    """
    if component in ("plasma", "cryoprecipitate"):
        compatible = is_plasma_compatible(
            donor_blood_type, donor_rh, recipient_blood_type, recipient_rh
        )
        rule_type = "plasma"
    else:
        compatible = is_rbc_compatible(
            donor_blood_type, donor_rh, recipient_blood_type, recipient_rh
        )
        rule_type = "rbc"

    donor_group = f"{donor_blood_type}{donor_rh}"
    recipient_group = f"{recipient_blood_type}{recipient_rh}"

    return {
        "compatible": compatible,
        "donor_group": donor_group,
        "recipient_group": recipient_group,
        "component": component,
        "rule_type": rule_type,
        "message": (
            f"{donor_group} est compatible avec {recipient_group} pour {component}"
            if compatible
            else f"{donor_group} est INCOMPATIBLE avec {recipient_group} pour {component}"
        ),
    }


def get_compatibility_matrix() -> dict:
    """Get the full ABO+Rh compatibility matrix for display.

    Returns a matrix showing which donor types can give to which recipient types,
    for both RBC and plasma products.
    """
    return get_full_compatibility_matrix()
