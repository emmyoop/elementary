import json
from pathlib import Path
from typing import Dict

import pytest

_REPORT_DATA_FILENAME = "elementary_output.json"
_REPORT_DATA_FIXTURE = Path(__file__).parent / "fixtures" / _REPORT_DATA_FILENAME
_REPORT_DATA_PATH = Path(_REPORT_DATA_FILENAME)

TotalsEntry = Dict[str, int]
Totals = Dict[str, TotalsEntry]


def test_report_keys(report_data_fixture):
    report_data = get_report_data()
    assert report_data.keys() == report_data_fixture.keys()


def test_totals(report_data_fixture):
    report_data = get_report_data()
    for key in report_data_fixture:
        if key.endswith("_totals"):
            assert_totals(report_data[key], report_data_fixture[key])


def test_sidebar(report_data_fixture):
    report_data = get_report_data()
    assert (
        "model.elementary_integration_tests.error_model"
        in report_data["sidebars"]["dbt"]["elementary_integration_tests"]["models"][
            "__files__"
        ]
    )
    assert (
        "model.elementary_integration_tests.nested"
        in report_data["sidebars"]["dbt"]["elementary_integration_tests"]["models"][
            "nested"
        ]["models"]["tree"]["__files__"]
    )
    assert (
        "source.elementary_integration_tests.training.any_type_column_anomalies_training"
        in report_data["sidebars"]["dbt"]["elementary_integration_tests"]["sources"][
            "__files__"
        ]
    )
    assert (
        "model.elementary_integration_tests.any_type_column_anomalies"
        in report_data["sidebars"]["owners"]["@edr"]
    )
    assert (
        "model.elementary_integration_tests.any_type_column_anomalies"
        not in report_data["sidebars"]["owners"]["No owners"]
    )
    assert (
        "model.elementary_integration_tests.string_column_anomalies"
        in report_data["sidebars"]["tags"]["marketing"]
    )
    assert (
        "model.elementary_integration_tests.string_column_anomalies"
        not in report_data["sidebars"]["tags"]["No tags"]
    )


def test_duplicate_rows_for_latest_run_status(report_data_fixture):
    report_data = get_report_data()
    # e2e contains 2 failed dimension tests and 1 passed
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="dimension_anomalies",
        status="fail",
        expected_ammount=2,
    )
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="dimension_anomalies",
        status="pass",
        expected_ammount=1,
    )

    # e2e contains 1 passed schema change test for groups table
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes",
        table="groups",
    )

    # e2e contains 3 failed schema change test for stats_player table
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes",
        table="stats_players",
        expected_ammount=3,
    )
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes",
        table="stats_players",
        column="offsides",
        expected_ammount=1,
    )
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes",
        table="stats_players",
        column="red_cards",
        expected_ammount=1,
    )
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes",
        table="stats_players",
        column="key_crosses",
        expected_ammount=1,
    )

    # e2e contains 1 passed schema change test for stats_team table
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes",
        table="stats_team",
    )

    # e2e contains 1 passed schema change test for string_column_anomalies table
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes",
        table="string_column_anomalies",
    )

    # e2e contains 1 passed schema change test for numeric_column_anomalies table
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes",
        table="numeric_column_anomalies",
    )

    # e2e contains only 4 singular failed tests
    assert_test_counter(
        report_data=report_data,
        test_type="dbt_test",
        test_sub_type="singular",
        status="fail",
        expected_ammount=4,
    )
    assert_test_counter(
        report_data=report_data,
        test_type="dbt_test",
        test_sub_type="singular",
        expected_ammount=4,
    )

    # e2e contains 2 failed and 1 error schema changes from baseline tests for groups table
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes_from_baseline",
        table="groups",
        status="fail",
        expected_ammount=2,
    )
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes_from_baseline",
        table="groups",
        status="error",
        expected_ammount=1,
    )

    # e2e contains 2 schema changes from baseline tests for goals column at stats_players table (2 different tests)
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes_from_baseline",
        table="stats_players",
        column="goals",
        expected_ammount=2,
    )

    # e2e contains 2 schema changes from baseline tests for coffee_cups_consumed column at stats_players table (2 different tests)
    assert_test_counter(
        report_data=report_data,
        test_type="schema_change",
        name="schema_changes_from_baseline",
        table="stats_players",
        column="coffee_cups_consumed",
        expected_ammount=2,
    )

    # e2e contains 56 all columns anomalies tests
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        expected_ammount=56,
    )
    # All of the tests are defined on the table any_type_column_anomalies
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        expected_ammount=56,
    )
    # updated_at column should have 2 passed test results.
    # 2 for any type column
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        column="updated_at",
        status="pass",
        expected_ammount=2,
    )
    # null_percent_str column should have 7 test results.
    # 5 for string type column, 2 for any type column
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        column="null_percent_str",
        expected_ammount=7,
    )
    # null_percent_int column should have 9 test results.
    # 7 for numeric type column, 2 for any type column
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        column="null_percent_int",
        expected_ammount=9,
    )
    # null_percent_float column should have 9 test results.
    # 7 for numeric type column, 2 for any type column
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        column="null_percent_float",
        expected_ammount=9,
    )
    # null_percent_bool column should have 2 passed test results.
    # 2 for any type column
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        column="null_percent_bool",
        expected_ammount=2,
    )
    # null_count_str column should have 7 test results.
    # 5 for string type column, 2 for any type column
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        column="null_count_str",
        expected_ammount=7,
    )
    # null_count_int column should have 9 test results.
    # 7 for numeric type column, 2 for any type column
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        column="null_count_int",
        expected_ammount=9,
    )
    # null_count_float column should have 9 test results.
    # 7 for numeric type column, 2 for any type column
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        column="null_count_float",
        expected_ammount=9,
    )
    # null_count_bool column should have 2 passed test results.
    # 2 for any type column
    assert_test_counter(
        report_data=report_data,
        test_type="anomaly_detection",
        name="all_columns_anomalies",
        table="any_type_column_anomalies",
        column="null_count_bool",
        expected_ammount=2,
    )


def assert_test_counter(
    report_data,
    test_type,
    table=None,
    column=None,
    test_sub_type=None,
    status=None,
    name=None,
    expected_ammount=1,
):
    test_results = report_data.get("test_results")
    tests_found = 0
    for tests in test_results.values():
        for test in tests:
            test_metadata = test.get("metadata")
            match_test_type = test_metadata.get("test_type") == test_type
            match_table = (
                test_metadata.get("table_name", "").lower() == table.lower()
                if table and test_metadata.get("table_name")
                else True
            )
            match_column = (
                test_metadata.get("column_name").lower() == column.lower()
                if column and test_metadata.get("column_name")
                else True
            )
            match_test_sub_type = (
                test_metadata.get("test_sub_type") == test_sub_type
                if test_sub_type
                else True
            )
            match_status = (
                test_metadata.get("latest_run_status") == status if status else True
            )
            match_name = test_metadata.get("test_name") == name if name else True
            if (
                match_test_type
                and match_table
                and match_column
                and match_test_sub_type
                and match_status
                and match_name
            ):
                tests_found += 1
    assert tests_found == expected_ammount


def assert_totals(data_totals: Totals, fixture_totals: Totals):
    for total_key in data_totals:
        assert_totals_entry(data_totals[total_key], fixture_totals[total_key])


def assert_totals_entry(
    data_total_entries: TotalsEntry, fixture_total_entries: TotalsEntry
):
    for key in data_total_entries:
        assert data_total_entries[key] * fixture_total_entries[key] >= 0


@pytest.fixture
def report_data_fixture():
    return json.loads(_REPORT_DATA_FIXTURE.read_text())


def get_report_data():
    return json.loads(_REPORT_DATA_PATH.read_text())
