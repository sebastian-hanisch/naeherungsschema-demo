"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mini():
    """Neun Pakete mit den Größen 8, 7, 6, 5, 4, 3, 2, 2, 1 (Nummern 0 bis 8), Kapazität 10, Gesamtgröße 38.

    Von Hand gerechnet (Details in tests/test_algorithm.py): FFD und das Optimum brauchen 4 Container, das Schema mit eps = 0,3 und zwei Gruppen 5: Die Rundung kostet einen Container."""
    return [8, 7, 6, 5, 4, 3, 2, 2, 1], 10
