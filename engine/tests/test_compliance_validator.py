"""Tests for compliance policy result contract validation."""

# pylint: disable=missing-function-docstring
import pytest

from validation.validator import (
    ResultContractError,
    validate_result_contract,
)


def test_valid_result_contract():
    result = {
        "compliant": True,
        "message": "Control passed",
        "details": {},
    }

    validate_result_contract(result)


def test_result_must_be_object():
    with pytest.raises(
        ResultContractError,
        match="Policy result must be a JSON object",
    ):
        validate_result_contract([])


def test_missing_required_field():
    result = {
        "compliant": True,
        "details": {},
    }

    with pytest.raises(
        ResultContractError,
        match="missing required field",
    ):
        validate_result_contract(result)


def test_compliant_must_be_boolean():
    result = {
        "compliant": "yes",
        "message": "Control passed",
        "details": {},
    }

    with pytest.raises(
        ResultContractError,
        match="'compliant' must be a boolean",
    ):
        validate_result_contract(result)


def test_message_must_be_string():
    result = {
        "compliant": True,
        "message": 123,
        "details": {},
    }

    with pytest.raises(
        ResultContractError,
        match="'message' must be a string",
    ):
        validate_result_contract(result)


def test_details_must_be_object():
    result = {
        "compliant": True,
        "message": "Control passed",
        "details": [],
    }

    with pytest.raises(
        ResultContractError,
        match="'details' must be an object",
    ):
        validate_result_contract(result)


def test_additional_fields_are_allowed():
    result = {
        "compliant": True,
        "message": "Control passed",
        "details": {},
        "extra_evidence": "allowed",
    }

    validate_result_contract(result)
