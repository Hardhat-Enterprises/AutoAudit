# backend/app/models/compliance_models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from ..db import Base  # assumes you have Base in backend/app/db.py

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    external_tenant_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Rule(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True)
    framework = Column(String(100), nullable=False)
    control_key = Column(String(100), nullable=False)
    title = Column(Text, nullable=False)
    severity = Column(String(20))
    description = Column(Text)

class Scan(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    status = Column(String(30), default="running")
    compliance_score = Column(Numeric(5,2))
    total_controls = Column(Integer, default=0)
    passed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    not_tested_count = Column(Integer, default=0)
    notes = Column(Text)

    tenant = relationship("Tenant", backref="scans")
    findings = relationship("Issue", backref="scan")

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("rules.id"))
    priority = Column(String(20))
    title = Column(Text)
    description = Column(Text)
    result = Column(String(20))
    evidence = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rule = relationship("Rule", backref="issues")
