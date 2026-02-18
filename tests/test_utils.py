import json

from rita.utils import deaccent, Node, ExtendedOp, flatten, Timer, timer, RitaJSONEncoder
from rita.config import SessionConfig


class TestDeaccent:
    def test_lithuanian(self):
        assert deaccent("Sarunas") == "Sarunas"
        assert deaccent("Kestutis") == "Kestutis"
        assert deaccent("Azuolas") == "Azuolas"

    def test_accented_lithuanian(self):
        assert deaccent("Šarūnas") == "Sarunas"
        assert deaccent("Kęstutis") == "Kestutis"
        assert deaccent("Ąžuolas") == "Azuolas"

    def test_french(self):
        assert deaccent("naïve") == "naive"
        assert deaccent("café") == "cafe"

    def test_no_change(self):
        assert deaccent("hello") == "hello"


class TestNode:
    def test_basic_creation(self):
        n = Node(data="test")
        assert n.data == "test"
        assert n.children == []
        assert n.next_node is None
        assert n.weight == 1

    def test_add_child(self):
        n = Node()
        n.add_child("a")
        n.add_child("b")
        assert n.weight == 2
        assert len(n.children) == 2

    def test_unwrap_no_children(self):
        n = Node(data="hello")
        results = list(n.unwrap())
        assert len(results) == 1
        assert results[0] == ["hello"]

    def test_unwrap_with_chain(self):
        n1 = Node(data="hello")
        n2 = Node(data="world")
        n1.add_next(n2)
        results = list(n1.unwrap())
        assert len(results) == 1
        assert results[0] == ["hello", "world"]

    def test_unwrap_with_branching(self):
        root = Node()
        branch = Node()
        branch.add_child("a")
        branch.add_child("b")
        root.add_next(branch)
        results = list(root.unwrap())
        assert len(results) == 2

    def test_repr(self):
        n = Node(data="test")
        r = repr(n)
        assert "test" in r

    def test_add_next(self):
        n1 = Node(data="first")
        n2 = Node(data="second")
        n1.add_next(n2)
        assert n1.next_node is n2


class TestExtendedOp:
    def test_from_string(self):
        op = ExtendedOp("+")
        assert op.value == "+"
        assert op.case_sensitive_override is False
        assert op.local_regex_override is False

    def test_from_none(self):
        op = ExtendedOp(None)
        assert op.value is None
        assert op.empty()

    def test_from_extended_op(self):
        original = ExtendedOp("+")
        original.case_sensitive_override = True
        original.local_regex_override = True
        copy = ExtendedOp(original)
        assert copy.value == "+"
        assert copy.case_sensitive_override is True
        assert copy.local_regex_override is True

    def test_empty_none(self):
        assert ExtendedOp(None).empty()

    def test_empty_blank(self):
        assert ExtendedOp("").empty()
        assert ExtendedOp("  ").empty()

    def test_not_empty(self):
        assert not ExtendedOp("+").empty()

    def test_eq_string(self):
        op = ExtendedOp("+")
        assert op == "+"
        assert op != "?"

    def test_eq_extended_op(self):
        op1 = ExtendedOp("+")
        op2 = ExtendedOp("+")
        assert op1 == op2

    def test_eq_different_flags(self):
        op1 = ExtendedOp("+")
        op2 = ExtendedOp("+")
        op2.case_sensitive_override = True
        assert op1 != op2

    def test_ignore_case_default(self):
        cfg = SessionConfig()
        op = ExtendedOp(None)
        assert op.ignore_case(cfg) is True

    def test_ignore_case_with_override(self):
        cfg = SessionConfig()
        op = ExtendedOp(None)
        op.case_sensitive_override = True
        assert op.ignore_case(cfg) is False

    def test_str_with_value(self):
        assert str(ExtendedOp("+")) == "+"

    def test_str_none(self):
        assert str(ExtendedOp(None)) == ""

    def test_repr(self):
        assert repr(ExtendedOp("+")) == "+"


class TestFlatten:
    def test_multi_item_returns_as_is(self):
        result = flatten(["a", "b", "c"])
        assert result == ["a", "b", "c"]

    def test_single_item_list(self):
        result = list(flatten([["a", "b"]]))
        assert "a" in result
        assert "b" in result

    def test_single_callable(self):
        result = list(flatten([lambda: ["x", "y"]]))
        assert "x" in result
        assert "y" in result

    def test_shallow(self):
        result = list(flatten(["a", "b"], shallow=True))
        assert "a" in result
        assert "b" in result


class TestTimer:
    def test_basic(self):
        t = Timer("test")
        delta = t.stop()
        assert isinstance(delta, int)
        assert delta >= 0

    def test_context_manager(self):
        with timer("test"):
            pass  # Should not raise


class TestRitaJSONEncoder:
    def test_encode_extended_op(self):
        encoder = RitaJSONEncoder()
        op = ExtendedOp("+")
        result = encoder.default(op)
        assert result == "+"

    def test_encode_extended_op_none(self):
        encoder = RitaJSONEncoder()
        op = ExtendedOp(None)
        result = encoder.default(op)
        assert result is None

    def test_full_json_encode(self):
        data = {"op": ExtendedOp("+")}
        result = json.dumps(data, cls=RitaJSONEncoder)
        assert '"+"' in result

    def test_encode_non_extended_op(self):
        encoder = RitaJSONEncoder()

        class Obj:
            def __init__(self):
                self.x = 1
                self.y = 2

        result = encoder.default(Obj())
        assert result == {"x": 1, "y": 2}
