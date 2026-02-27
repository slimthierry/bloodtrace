"""Tests for blood compatibility rules."""

import pytest

from app.utils.blood_compatibility import (
    is_rbc_compatible,
    is_plasma_compatible,
    get_compatible_donor_types,
    get_full_compatibility_matrix,
)


class TestRBCCompatibility:
    """Tests for RBC (Red Blood Cell) compatibility rules."""

    def test_o_negative_is_universal_donor(self):
        """O- can donate RBC to any blood type."""
        recipients = [
            ("O", "+"), ("O", "-"),
            ("A", "+"), ("A", "-"),
            ("B", "+"), ("B", "-"),
            ("AB", "+"), ("AB", "-"),
        ]
        for bt, rh in recipients:
            assert is_rbc_compatible("O", "-", bt, rh), f"O- should be compatible with {bt}{rh}"

    def test_ab_positive_is_universal_recipient(self):
        """AB+ can receive RBC from any blood type."""
        donors = [
            ("O", "+"), ("O", "-"),
            ("A", "+"), ("A", "-"),
            ("B", "+"), ("B", "-"),
            ("AB", "+"), ("AB", "-"),
        ]
        for bt, rh in donors:
            assert is_rbc_compatible(bt, rh, "AB", "+"), f"{bt}{rh} should be compatible with AB+"

    def test_same_type_always_compatible(self):
        """Same blood type is always compatible."""
        types = [
            ("O", "+"), ("O", "-"),
            ("A", "+"), ("A", "-"),
            ("B", "+"), ("B", "-"),
            ("AB", "+"), ("AB", "-"),
        ]
        for bt, rh in types:
            assert is_rbc_compatible(bt, rh, bt, rh), f"{bt}{rh} should be self-compatible"

    def test_rh_positive_cannot_donate_to_rh_negative(self):
        """Rh+ blood cannot be given to Rh- recipients."""
        assert not is_rbc_compatible("A", "+", "A", "-")
        assert not is_rbc_compatible("O", "+", "O", "-")
        assert not is_rbc_compatible("B", "+", "B", "-")

    def test_incompatible_abo_types(self):
        """Verify known incompatibilities."""
        assert not is_rbc_compatible("A", "+", "B", "+")
        assert not is_rbc_compatible("B", "+", "A", "+")
        assert not is_rbc_compatible("A", "+", "O", "+")
        assert not is_rbc_compatible("AB", "+", "O", "+")

    def test_a_compatibility(self):
        """Test A type compatibility rules."""
        assert is_rbc_compatible("A", "-", "A", "+")
        assert is_rbc_compatible("A", "-", "A", "-")
        assert is_rbc_compatible("A", "+", "A", "+")
        assert is_rbc_compatible("O", "-", "A", "+")
        assert is_rbc_compatible("O", "+", "A", "+")

    def test_b_compatibility(self):
        """Test B type compatibility rules."""
        assert is_rbc_compatible("B", "-", "B", "+")
        assert is_rbc_compatible("B", "-", "B", "-")
        assert is_rbc_compatible("B", "+", "B", "+")
        assert is_rbc_compatible("O", "-", "B", "+")


class TestPlasmaCompatibility:
    """Tests for plasma compatibility rules (inverted from RBC)."""

    def test_ab_is_universal_plasma_donor(self):
        """AB+ can donate plasma to AB+ only (most restrictive)."""
        # AB+ is universal donor for plasma (can give to all)
        # Wait, plasma rules are inverted: AB gives to everyone
        # Actually in the matrix: O- can RECEIVE from everyone for plasma
        assert is_plasma_compatible("AB", "+", "O", "+")
        assert is_plasma_compatible("AB", "+", "A", "+")
        assert is_plasma_compatible("AB", "+", "B", "+")

    def test_o_is_universal_plasma_recipient(self):
        """O- can receive plasma from any type."""
        donors = [
            ("O", "+"), ("O", "-"),
            ("A", "+"), ("A", "-"),
            ("B", "+"), ("B", "-"),
            ("AB", "+"), ("AB", "-"),
        ]
        for bt, rh in donors:
            assert is_plasma_compatible(bt, rh, "O", "-"), (
                f"{bt}{rh} plasma should be compatible with O-"
            )


class TestCompatibleDonorTypes:
    """Tests for getting compatible donor type lists."""

    def test_ab_positive_gets_all_donors(self):
        """AB+ recipient should have all 8 blood types as compatible RBC donors."""
        donors = get_compatible_donor_types("AB", "+", "packed_rbc")
        assert len(donors) == 8

    def test_o_negative_gets_only_self(self):
        """O- recipient can only receive from O- for RBC."""
        donors = get_compatible_donor_types("O", "-", "packed_rbc")
        assert len(donors) == 1
        assert ("O", "-") in donors

    def test_plasma_compatibility_inverted(self):
        """Plasma compatibility should be inverted from RBC."""
        # O- can receive plasma from everyone
        plasma_donors = get_compatible_donor_types("O", "-", "plasma")
        assert len(plasma_donors) == 8


class TestFullCompatibilityMatrix:
    """Tests for the complete compatibility matrix."""

    def test_matrix_structure(self):
        """Test that the matrix contains all expected keys."""
        matrix = get_full_compatibility_matrix()
        assert "rbc" in matrix
        assert "plasma" in matrix
        assert "blood_groups" in matrix
        assert len(matrix["blood_groups"]) == 8

    def test_all_groups_present_in_rbc(self):
        """All 8 blood groups should be in the RBC matrix."""
        matrix = get_full_compatibility_matrix()
        assert len(matrix["rbc"]) == 8

    def test_all_groups_present_in_plasma(self):
        """All 8 blood groups should be in the plasma matrix."""
        matrix = get_full_compatibility_matrix()
        assert len(matrix["plasma"]) == 8

    def test_universal_donor_flagged(self):
        """O- should be flagged as universal donor in RBC matrix."""
        matrix = get_full_compatibility_matrix()
        assert matrix["rbc"]["O-"]["is_universal_donor"] is True

    def test_universal_recipient_flagged(self):
        """AB+ should be flagged as universal recipient in RBC matrix."""
        matrix = get_full_compatibility_matrix()
        assert matrix["rbc"]["AB+"]["is_universal_recipient"] is True
