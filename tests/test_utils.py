from rita.utils import deaccent


class TestDeaccent(object):
    def test_lithuanian(self):
        assert deaccent("Šarūnas") == "Sarunas"
        assert deaccent("Kęstutis") == "Kestutis"
        assert deaccent("Ąžuolas") == "Azuolas"


def test():
    rules = """
    cuts = {"fitted", "wide-cut"}
    lengths = {"short", "long", "calf-length", "knee-length"}
    fabric_types = {"soft", "airy", "crinkled"}
    fabrics = {"velour", "chiffon", "knit", "woven", "stretch"}

    {IN_LIST(cuts)?, IN_LIST(lengths), WORD("dress")}->MARK("DRESS_TYPE")
    {IN_LIST(lengths), IN_LIST(cuts), WORD("dress")}->MARK("DRESS_TYPE")
    {IN_LIST(fabric_types)?, IN_LIST(fabrics)}->MARK("DRESS_FABRIC")
    """
