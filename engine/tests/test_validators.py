"""Tests for tenant_id validation (PowerShell command injection prevention)."""

import pytest

from worker.validators import validate_tenant_id


# -- Valid inputs: should return the stripped value without raising --

VALID_TENANT_IDS = [
    # GUIDs
    ("12345678-1234-1234-1234-123456789abc", "12345678-1234-1234-1234-123456789abc"),
    ("ABCDEF01-2345-6789-ABCD-EF0123456789", "ABCDEF01-2345-6789-ABCD-EF0123456789"),
    ("aAbBcCdD-1234-5678-9012-eEfF00112233", "aAbBcCdD-1234-5678-9012-eEfF00112233"),
    # GUIDs with surrounding whitespace (should be stripped)
    ("  12345678-1234-1234-1234-123456789abc  ", "12345678-1234-1234-1234-123456789abc"),
    # Domain names
    ("contoso.onmicrosoft.com", "contoso.onmicrosoft.com"),
    ("tenant.contoso.com", "tenant.contoso.com"),
    ("example.co", "example.co"),
    ("my-tenant.onmicrosoft.com", "my-tenant.onmicrosoft.com"),
    ("sub1.sub2.example.com", "sub1.sub2.example.com"),
    # Domain with surrounding whitespace
    ("  contoso.onmicrosoft.com  ", "contoso.onmicrosoft.com"),
]


@pytest.mark.parametrize("input_val,expected", VALID_TENANT_IDS)
def test_valid_tenant_id(input_val: str, expected: str) -> None:
    assert validate_tenant_id(input_val) == expected


# -- Invalid inputs: should raise ValueError --

INVALID_TENANT_IDS = [
    # Empty / whitespace
    "",
    "   ",
    # PowerShell injection via GUID breakout
    '12345678-1234-1234-1234-123456789abc"; Remove-Mailbox',
    # PowerShell injection via domain breakout
    'contoso.com"; Remove-Mailbox -Identity admin -Confirm:$false; #',
    # Semicolon injection
    "contoso.com; whoami",
    # PowerShell subexpression
    '$(Invoke-Expression "bad")',
    # Backtick injection
    '`Invoke-Expression "bad"',
    # Pipe injection
    "valid.com | bad-command",
    # Newline injection
    "valid.com\nInvoke-Expression bad",
    # GUID without hyphens
    "12345678123412341234123456789abc",
    # Partial GUID
    "12345678-1234-1234-1234",
    # GUID with extra segment
    "12345678-1234-1234-1234-123456789abc-extra",
    # Domain starting with hyphen
    "-invalid.com",
    # Domain ending with hyphen
    "invalid-.com",
    # Domain with single-char TLD
    "invalid.c",
    # Domain with underscore
    "under_score.com",
    # Domain with no TLD
    "localhost",
    # Bare special characters
    '"',
    "$",
    ";",
]


@pytest.mark.parametrize("input_val", INVALID_TENANT_IDS)
def test_invalid_tenant_id(input_val: str) -> None:
    with pytest.raises(ValueError, match="tenant_id"):
        validate_tenant_id(input_val)
