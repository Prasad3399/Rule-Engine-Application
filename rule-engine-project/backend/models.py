class Node:
    def __init__(self, type, operator=None, value=None, left=None, right=None):
        self.type = type  # "operator" or "operand"
        self.operator = operator
        self.value = value
        self.left = left
        self.right = right

    def to_dict(self):
        return {
            "type": self.type,
            "operator": self.operator,
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
        }

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return Node(
            type=data["type"],
            operator=data.get("operator"),
            value=data.get("value"),
            left=Node.from_dict(data.get("left")),
            right=Node.from_dict(data.get("right")),
        )

    def evaluate(self, data):
        if self.type == "operand":
            attr, op, value = self.value["attribute"], self.value["operator"], self.value["value"]
            return eval(f"{data[attr]} {op} {value}")

        left_eval = self.left.evaluate(data) if self.left else False
        right_eval = self.right.evaluate(data) if self.right else False

        if self.operator == "AND":
            return left_eval and right_eval
        if self.operator == "OR":
            return left_eval or right_eval
        raise ValueError("Invalid operator")

    @staticmethod
    def combine_rules(rules, operator="AND"):
        root = Node("operator", operator=operator)
        left = rules[0]
        for rule in rules[1:]:
            left = Node("operator", operator=operator, left=left, right=rule)
        root.left = left
        return root

    @staticmethod
    def parse_rule_string(rule_string):
        tokens = rule_string.split()
        return Node("operand", value={"attribute": tokens[0], "operator": tokens[1], "value": tokens[2]})
