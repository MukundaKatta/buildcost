"""Tests for Buildcost."""
from src.core import Buildcost
def test_init(): assert Buildcost().get_stats()["ops"] == 0
def test_op(): c = Buildcost(); c.generate(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Buildcost(); [c.generate() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Buildcost(); c.generate(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Buildcost(); r = c.generate(); assert r["service"] == "buildcost"
