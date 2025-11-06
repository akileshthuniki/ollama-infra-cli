# Security group for a service
resource "aws_security_group" "this" {
  name        = var.name
  description = var.description
  vpc_id      = var.vpc_id

  tags = merge(var.tags, {
    Name = var.name
  })
}

# Ingress rules
resource "aws_security_group_rule" "ingress" {
  count = length(var.ingress_rules)

  type              = "ingress"
  from_port         = var.ingress_rules[count.index].from_port
  to_port           = var.ingress_rules[count.index].to_port
  protocol          = var.ingress_rules[count.index].protocol
  cidr_blocks       = lookup(var.ingress_rules[count.index], "cidr_blocks", null)
  security_group_id = aws_security_group.this.id
  source_security_group_id = lookup(var.ingress_rules[count.index], "source_security_group_id", null)
  description       = lookup(var.ingress_rules[count.index], "description", null)
  self              = lookup(var.ingress_rules[count.index], "self", null)
}

# Egress rules
resource "aws_security_group_rule" "egress" {
  count = length(var.egress_rules)

  type              = "egress"
  from_port         = var.egress_rules[count.index].from_port
  to_port           = var.egress_rules[count.index].to_port
  protocol          = var.egress_rules[count.index].protocol
  cidr_blocks       = lookup(var.egress_rules[count.index], "cidr_blocks", null)
  security_group_id = aws_security_group.this.id
  description       = lookup(var.egress_rules[count.index], "description", null)
}
