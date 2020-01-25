from rita.utils import deaccent


class TestDeaccent(object):
    def test_lithuanian(self):
        assert deaccent("Šarūnas") == "Sarunas"
        assert deaccent("Kęstutis") == "Kestutis"
        assert deaccent("Ąžuolas") == "Azuolas"
