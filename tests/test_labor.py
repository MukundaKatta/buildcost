"""Tests for labor rate database."""

import pytest
from buildcost.estimator.labor import LaborRateDatabase, REGIONAL_MULTIPLIERS
from buildcost.models import Region


class TestLaborRateDatabase:
    def test_default_region(self):
        db = LaborRateDatabase()
        assert db.region == Region.SOUTHEAST

    def test_get_rate_carpenter(self):
        db = LaborRateDatabase(Region.SOUTHEAST)
        rate = db.get_rate("carpenter")
        assert rate > 0
        # SE multiplier is 0.90, base is 42
        assert rate == pytest.approx(42 * 0.90, rel=0.01)

    def test_regional_differences(self):
        rate_se = LaborRateDatabase(Region.SOUTHEAST).get_rate("electrician")
        rate_ne = LaborRateDatabase(Region.NORTHEAST).get_rate("electrician")
        assert rate_ne > rate_se  # NE is more expensive

    def test_unknown_trade(self):
        db = LaborRateDatabase()
        with pytest.raises(ValueError):
            db.get_rate("astronaut")

    def test_get_rate_info(self):
        db = LaborRateDatabase(Region.WEST)
        info = db.get_rate_info("plumber")
        assert info["title"] == "Plumber"
        assert info["region"] == "west"
        assert info["regional_rate"] > info["base_rate"]

    def test_get_all_rates(self):
        db = LaborRateDatabase()
        rates = db.get_all_rates()
        assert len(rates) >= 20
        for rate in rates.values():
            assert rate > 0

    def test_list_trades(self):
        db = LaborRateDatabase()
        trades = db.list_trades()
        assert "carpenter" in trades
        assert "electrician" in trades
        assert "plumber" in trades
        assert len(trades) >= 20

    def test_search_trades(self):
        db = LaborRateDatabase()
        results = db.search_trades("electric")
        assert len(results) >= 1

    def test_compare_regions(self):
        comparison = LaborRateDatabase.compare_regions("carpenter")
        assert len(comparison) == len(Region)
        # West should be highest
        assert comparison["west"] > comparison["southeast"]

    def test_all_regions_have_multipliers(self):
        for region in Region:
            assert region in REGIONAL_MULTIPLIERS
