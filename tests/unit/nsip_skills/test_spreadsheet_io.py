"""
Unit tests for nsip_skills.common.spreadsheet_io

Tests:
- Column name normalization
- Column mapping detection
- CSV/Excel reading and writing
- Google Sheets reading (mocked)
- FlockRecord extraction
- Auto-format detection
- Error handling

Target: >95% coverage
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from nsip_skills.common.spreadsheet_io import (
    SpreadsheetData,
    detect_column_mapping,
    extract_flock_records,
    find_lpn_column,
    normalize_column_name,
    read_csv,
    read_excel,
    read_google_sheets,
    read_spreadsheet,
    write_csv,
    write_excel,
    write_spreadsheet,
)


class TestNormalizeColumnName:
    """Tests for normalize_column_name function."""

    def test_lowercase(self):
        """Verify uppercase is converted to lowercase."""
        assert normalize_column_name("LPN_ID") == "lpn_id"

    def test_spaces_to_underscores(self):
        """Verify spaces are converted to underscores."""
        assert normalize_column_name("Animal Name") == "animal_name"

    def test_special_characters_removed(self):
        """Verify special characters are removed."""
        assert normalize_column_name("LPN-ID!") == "lpn_id"

    def test_mixed_case_and_spaces(self):
        """Verify mixed case and spaces are handled."""
        assert normalize_column_name("Date Of Birth") == "date_of_birth"

    def test_leading_trailing_underscores_stripped(self):
        """Verify leading/trailing underscores are stripped."""
        assert normalize_column_name("__test__") == "test"

    def test_multiple_special_chars(self):
        """Verify multiple special characters become single underscore."""
        assert normalize_column_name("a--b!!c") == "a_b_c"


class TestFindLpnColumn:
    """Tests for find_lpn_column function."""

    def test_lpn_id_found(self):
        """Verify LPN_ID column is found."""
        columns = ["Name", "LPN_ID", "Tag"]
        assert find_lpn_column(columns) == "LPN_ID"

    def test_lpnid_found(self):
        """Verify LPNID (no underscore) is found."""
        columns = ["Name", "LPNID", "Tag"]
        assert find_lpn_column(columns) == "LPNID"

    def test_lpn_found(self):
        """Verify LPN is found."""
        columns = ["Name", "LPN", "Tag"]
        assert find_lpn_column(columns) == "LPN"

    def test_id_found(self):
        """Verify ID column is found."""
        columns = ["Name", "ID", "Tag"]
        assert find_lpn_column(columns) == "ID"

    def test_animal_id_found(self):
        """Verify Animal_ID is found."""
        columns = ["Name", "Animal_ID", "Tag"]
        assert find_lpn_column(columns) == "Animal_ID"

    def test_nsip_id_found(self):
        """Verify NSIP_ID is found."""
        columns = ["Name", "NSIP_ID", "Tag"]
        assert find_lpn_column(columns) == "NSIP_ID"

    def test_not_found(self):
        """Verify None returned when no LPN column found."""
        columns = ["Name", "Tag", "Notes"]
        assert find_lpn_column(columns) is None

    def test_empty_list(self):
        """Verify None returned for empty list."""
        assert find_lpn_column([]) is None


class TestDetectColumnMapping:
    """Tests for detect_column_mapping function."""

    def test_full_mapping(self):
        """Verify all column types are detected."""
        columns = ["LPN_ID", "Tag", "Notes", "Group"]
        mapping = detect_column_mapping(columns)

        assert mapping["LPN_ID"] == "lpn_id"
        assert mapping["Tag"] == "local_id"
        assert mapping["Notes"] == "notes"
        assert mapping["Group"] == "group"

    def test_lpn_id_mapping(self):
        """Verify LPN ID column is mapped."""
        columns = ["LPN_ID", "Other"]
        mapping = detect_column_mapping(columns)
        assert mapping["LPN_ID"] == "lpn_id"

    def test_local_id_variations(self):
        """Verify local ID variations are detected."""
        for col in ["Tag", "Ear_Tag", "Name", "Animal_Name"]:
            mapping = detect_column_mapping([col])
            assert col in mapping
            assert mapping[col] == "local_id"

    def test_notes_variations(self):
        """Verify notes variations are detected."""
        for col in ["Notes", "Note", "Comments", "Remarks"]:
            mapping = detect_column_mapping([col])
            assert col in mapping
            assert mapping[col] == "notes"

    def test_group_variations(self):
        """Verify group variations are detected."""
        for col in ["Group", "Pen", "Pasture", "Lot", "Category"]:
            mapping = detect_column_mapping([col])
            assert col in mapping
            assert mapping[col] == "group"

    def test_empty_columns(self):
        """Verify empty column list returns empty mapping."""
        mapping = detect_column_mapping([])
        assert mapping == {}

    def test_unknown_columns_not_mapped(self):
        """Verify unknown columns are not in mapping."""
        columns = ["Unknown1", "Unknown2"]
        mapping = detect_column_mapping(columns)
        assert mapping == {}


class TestSpreadsheetData:
    """Tests for SpreadsheetData dataclass."""

    def test_basic_creation(self):
        """Verify basic dataclass creation."""
        data = SpreadsheetData(
            rows=[{"a": 1}],
            source="test.csv",
            source_type="csv",
        )
        assert data.rows == [{"a": 1}]
        assert data.source == "test.csv"
        assert data.source_type == "csv"
        assert data.sheet_name is None
        assert data.column_mapping is None

    def test_with_all_fields(self):
        """Verify all fields are preserved."""
        data = SpreadsheetData(
            rows=[{"a": 1}],
            source="test.xlsx",
            source_type="excel",
            sheet_name="Sheet1",
            column_mapping={"A": "a"},
        )
        assert data.sheet_name == "Sheet1"
        assert data.column_mapping == {"A": "a"}


class TestReadCsv:
    """Tests for read_csv function."""

    def test_basic_read(self, tmp_path):
        """Verify basic CSV reading."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("LPN_ID,Name,Tag\n123,Ram A,001\n456,Ewe B,002\n")

        result = read_csv(csv_file)

        assert result.source_type == "csv"
        assert len(result.rows) == 2
        assert result.rows[0]["LPN_ID"] == "123"
        assert result.rows[0]["Name"] == "Ram A"

    def test_column_mapping_detected(self, tmp_path):
        """Verify column mapping is detected."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("LPN_ID,Tag,Notes\n123,001,Test notes\n")

        result = read_csv(csv_file)

        assert "LPN_ID" in result.column_mapping
        assert result.column_mapping["LPN_ID"] == "lpn_id"

    def test_utf8_bom_handled(self, tmp_path):
        """Verify UTF-8 BOM is handled."""
        csv_file = tmp_path / "test.csv"
        # Write with UTF-8 BOM
        with open(csv_file, "w", encoding="utf-8-sig") as f:
            f.write("LPN_ID,Name\n123,Test\n")

        result = read_csv(csv_file)

        assert result.rows[0]["LPN_ID"] == "123"

    def test_file_not_found(self, tmp_path):
        """Verify FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            read_csv(tmp_path / "nonexistent.csv")

    def test_empty_csv(self, tmp_path):
        """Verify empty CSV is handled."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("LPN_ID,Name\n")

        result = read_csv(csv_file)

        assert result.rows == []

    def test_source_path_stored(self, tmp_path):
        """Verify source path is stored."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("LPN_ID\n123\n")

        result = read_csv(csv_file)

        assert str(csv_file) == result.source


class TestReadExcel:
    """Tests for read_excel function."""

    def test_basic_read(self, tmp_path):
        """Verify basic Excel reading."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        excel_file = tmp_path / "test.xlsx"
        df = pd.DataFrame({"LPN_ID": ["123", "456"], "Name": ["Ram A", "Ewe B"]})
        df.to_excel(excel_file, index=False)

        result = read_excel(excel_file)

        assert result.source_type == "excel"
        assert len(result.rows) == 2
        # Note: pandas may read numeric strings as integers
        assert str(result.rows[0]["LPN_ID"]) == "123"

    def test_sheet_name_by_index(self, tmp_path):
        """Verify sheet selection by index."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        excel_file = tmp_path / "test.xlsx"
        df = pd.DataFrame({"LPN_ID": ["123"]})
        df.to_excel(excel_file, index=False)

        result = read_excel(excel_file, sheet_name=0)

        assert len(result.rows) == 1

    def test_sheet_name_by_name(self, tmp_path):
        """Verify sheet selection by name."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        excel_file = tmp_path / "test.xlsx"
        with pd.ExcelWriter(excel_file) as writer:
            df = pd.DataFrame({"LPN_ID": ["123"]})
            df.to_excel(writer, sheet_name="Animals", index=False)

        result = read_excel(excel_file, sheet_name="Animals")

        assert result.sheet_name == "Animals"

    def test_file_not_found(self, tmp_path):
        """Verify FileNotFoundError for missing file."""
        pytest.importorskip("openpyxl")
        with pytest.raises(FileNotFoundError):
            read_excel(tmp_path / "nonexistent.xlsx")

    def test_import_error_without_pandas(self, tmp_path):
        """Verify ImportError when pandas not available."""
        with patch.dict("sys.modules", {"pandas": None}):
            with patch("builtins.__import__", side_effect=ImportError("No pandas")):
                with pytest.raises(ImportError) as exc_info:
                    read_excel(tmp_path / "test.xlsx")
                assert "pandas" in str(exc_info.value)


class TestReadGoogleSheets:
    """Tests for read_google_sheets function."""

    def test_basic_read(self):
        """Verify Google Sheets reading with mocked gspread."""
        with patch.dict("sys.modules", {"gspread": MagicMock()}):
            import sys

            mock_gspread = sys.modules["gspread"]
            mock_gc = MagicMock()
            mock_gspread.service_account.return_value = mock_gc

            mock_spreadsheet = MagicMock()
            mock_worksheet = MagicMock()
            mock_worksheet.title = "Sheet1"
            mock_worksheet.get_all_records.return_value = [{"LPN_ID": "123", "Name": "Ram A"}]
            mock_spreadsheet.sheet1 = mock_worksheet
            mock_gc.open_by_key.return_value = mock_spreadsheet

            result = read_google_sheets("https://docs.google.com/spreadsheets/d/abc123/edit")

            assert result.source_type == "gsheets"
            assert result.sheet_name == "Sheet1"
            assert len(result.rows) == 1

    def test_specific_sheet_name(self):
        """Verify specific sheet selection."""
        with patch.dict("sys.modules", {"gspread": MagicMock()}):
            import sys

            mock_gspread = sys.modules["gspread"]
            mock_gc = MagicMock()
            mock_gspread.service_account.return_value = mock_gc

            mock_spreadsheet = MagicMock()
            mock_worksheet = MagicMock()
            mock_worksheet.title = "Flock Data"
            mock_worksheet.get_all_records.return_value = [{"LPN_ID": "123"}]
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_gc.open_by_key.return_value = mock_spreadsheet

            result = read_google_sheets(
                "https://docs.google.com/spreadsheets/d/abc123/edit",
                sheet_name="Flock Data",
            )

            mock_spreadsheet.worksheet.assert_called_with("Flock Data")
            assert result.sheet_name == "Flock Data"

    def test_invalid_url(self):
        """Verify ValueError for invalid URL."""
        with patch.dict("sys.modules", {"gspread": MagicMock()}):
            with pytest.raises(ValueError) as exc_info:
                read_google_sheets("https://example.com/not-a-sheet")
            assert "Invalid Google Sheets URL" in str(exc_info.value)

    def test_import_error_without_gspread(self):
        """Verify ImportError when gspread not available."""
        with patch.dict("sys.modules", {"gspread": None}):
            with patch("builtins.__import__", side_effect=ImportError("No gspread")):
                with pytest.raises(ImportError) as exc_info:
                    read_google_sheets("https://docs.google.com/spreadsheets/d/abc/edit")
                assert "gspread" in str(exc_info.value)

    def test_empty_sheet(self):
        """Verify empty sheet handling."""
        with patch.dict("sys.modules", {"gspread": MagicMock()}):
            import sys

            mock_gspread = sys.modules["gspread"]
            mock_gc = MagicMock()
            mock_gspread.service_account.return_value = mock_gc

            mock_spreadsheet = MagicMock()
            mock_worksheet = MagicMock()
            mock_worksheet.title = "Empty"
            mock_worksheet.get_all_records.return_value = []
            mock_spreadsheet.sheet1 = mock_worksheet
            mock_gc.open_by_key.return_value = mock_spreadsheet

            result = read_google_sheets("https://docs.google.com/spreadsheets/d/abc123/edit")

            assert result.rows == []
            assert result.column_mapping == {}


class TestReadSpreadsheet:
    """Tests for read_spreadsheet function."""

    def test_csv_by_extension(self, tmp_path):
        """Verify CSV detection by extension."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("LPN_ID\n123\n")

        result = read_spreadsheet(csv_file)

        assert result.source_type == "csv"

    def test_excel_by_extension(self, tmp_path):
        """Verify Excel detection by extension."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        excel_file = tmp_path / "test.xlsx"
        df = pd.DataFrame({"LPN_ID": ["123"]})
        df.to_excel(excel_file, index=False)

        result = read_spreadsheet(excel_file)

        assert result.source_type == "excel"

    def test_xls_extension(self, tmp_path):
        """Verify .xls extension is detected as Excel."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        # Create xlsx and rename for test - modern pandas handles this gracefully
        xlsx_file = tmp_path / "temp.xlsx"
        xls_file = tmp_path / "test.xls"
        df = pd.DataFrame({"LPN_ID": ["123"]})
        df.to_excel(xlsx_file, index=False)
        xlsx_file.rename(xls_file)

        # Modern pandas auto-detects format, so this should work
        result = read_spreadsheet(xls_file)
        assert result.source_type == "excel"
        assert len(result.rows) == 1

    def test_google_sheets_url(self):
        """Verify Google Sheets URL detection."""
        with patch("nsip_skills.common.spreadsheet_io.read_google_sheets") as mock_read:
            mock_read.return_value = SpreadsheetData(rows=[], source="url", source_type="gsheets")

            result = read_spreadsheet("https://docs.google.com/spreadsheets/d/abc123/edit")

            assert result.source_type == "gsheets"
            mock_read.assert_called_once()

    def test_sheet_name_passed_to_excel(self, tmp_path):
        """Verify sheet_name is passed to Excel reader."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        excel_file = tmp_path / "test.xlsx"
        df = pd.DataFrame({"LPN_ID": ["123"]})
        df.to_excel(excel_file, index=False)

        result = read_spreadsheet(excel_file, sheet_name=0)

        assert result.source_type == "excel"

    def test_unknown_extension_defaults_csv(self, tmp_path):
        """Verify unknown extension defaults to CSV."""
        unknown_file = tmp_path / "test.txt"
        unknown_file.write_text("LPN_ID\n123\n")

        result = read_spreadsheet(unknown_file)

        assert result.source_type == "csv"

    def test_zip_signature_detection(self, tmp_path):
        """Verify XLSX detection by ZIP signature."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        # Create xlsx file without extension
        xlsx_file = tmp_path / "data"
        temp_xlsx = tmp_path / "temp.xlsx"
        df = pd.DataFrame({"LPN_ID": ["123"]})
        df.to_excel(temp_xlsx, index=False)
        temp_xlsx.rename(xlsx_file)

        result = read_spreadsheet(xlsx_file)

        assert result.source_type == "excel"


class TestExtractFlockRecords:
    """Tests for extract_flock_records function."""

    def test_basic_extraction(self):
        """Verify basic FlockRecord extraction."""
        data = SpreadsheetData(
            rows=[
                {"LPN_ID": "123", "Tag": "001", "Notes": "Test"},
                {"LPN_ID": "456", "Tag": "002", "Notes": ""},
            ],
            source="test.csv",
            source_type="csv",
            column_mapping={"LPN_ID": "lpn_id", "Tag": "local_id", "Notes": "notes"},
        )

        records = extract_flock_records(data)

        assert len(records) == 2
        assert records[0].lpn_id == "123"
        assert records[0].local_id == "001"
        assert records[0].notes == "Test"
        assert records[0].row_number == 1

    def test_empty_rows_skipped(self):
        """Verify rows with empty LPN are skipped."""
        data = SpreadsheetData(
            rows=[
                {"LPN_ID": "123"},
                {"LPN_ID": ""},
                {"LPN_ID": "  "},
                {"LPN_ID": "456"},
            ],
            source="test.csv",
            source_type="csv",
            column_mapping={"LPN_ID": "lpn_id"},
        )

        records = extract_flock_records(data)

        assert len(records) == 2
        assert records[0].lpn_id == "123"
        assert records[1].lpn_id == "456"

    def test_no_mapping_falls_back_to_detection(self):
        """Verify column detection when no mapping provided."""
        data = SpreadsheetData(
            rows=[{"LPN_ID": "123", "Tag": "001"}],
            source="test.csv",
            source_type="csv",
            column_mapping=None,
        )

        records = extract_flock_records(data)

        assert len(records) == 1
        assert records[0].lpn_id == "123"

    def test_no_lpn_column_raises(self):
        """Verify ValueError when no LPN column found."""
        data = SpreadsheetData(
            rows=[{"Name": "Test", "Tag": "001"}],
            source="test.csv",
            source_type="csv",
            column_mapping={},
        )

        with pytest.raises(ValueError) as exc_info:
            extract_flock_records(data)
        assert "Could not identify LPN ID column" in str(exc_info.value)

    def test_optional_fields(self):
        """Verify optional fields are None when not present."""
        data = SpreadsheetData(
            rows=[{"LPN_ID": "123"}],
            source="test.csv",
            source_type="csv",
            column_mapping={"LPN_ID": "lpn_id"},
        )

        records = extract_flock_records(data)

        assert records[0].local_id is None
        assert records[0].notes is None
        assert records[0].group is None

    def test_group_column_extracted(self):
        """Verify group column is extracted."""
        data = SpreadsheetData(
            rows=[{"LPN_ID": "123", "Pen": "A1"}],
            source="test.csv",
            source_type="csv",
            column_mapping={"LPN_ID": "lpn_id", "Pen": "group"},
        )

        records = extract_flock_records(data)

        assert records[0].group == "A1"

    def test_whitespace_stripped(self):
        """Verify whitespace is stripped from values."""
        data = SpreadsheetData(
            rows=[{"LPN_ID": "  123  ", "Tag": "  001  "}],
            source="test.csv",
            source_type="csv",
            column_mapping={"LPN_ID": "lpn_id", "Tag": "local_id"},
        )

        records = extract_flock_records(data)

        assert records[0].lpn_id == "123"
        assert records[0].local_id == "001"

    def test_row_numbers_sequential(self):
        """Verify row numbers are 1-indexed and sequential."""
        data = SpreadsheetData(
            rows=[
                {"LPN_ID": "123"},
                {"LPN_ID": "456"},
                {"LPN_ID": "789"},
            ],
            source="test.csv",
            source_type="csv",
            column_mapping={"LPN_ID": "lpn_id"},
        )

        records = extract_flock_records(data)

        assert [r.row_number for r in records] == [1, 2, 3]


class TestWriteCsv:
    """Tests for write_csv function."""

    def test_basic_write(self, tmp_path):
        """Verify basic CSV writing."""
        output_file = tmp_path / "output.csv"
        records = [
            {"LPN_ID": "123", "Name": "Ram A"},
            {"LPN_ID": "456", "Name": "Ewe B"},
        ]

        write_csv(records, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "LPN_ID" in content
        assert "123" in content
        assert "Ram A" in content

    def test_empty_records(self, tmp_path):
        """Verify empty records produces no file write."""
        output_file = tmp_path / "empty.csv"

        write_csv([], output_file)

        assert not output_file.exists()

    def test_custom_column_order(self, tmp_path):
        """Verify custom column order is respected."""
        output_file = tmp_path / "output.csv"
        records = [{"A": 1, "B": 2, "C": 3}]

        write_csv(records, output_file, columns=["C", "A", "B"])

        content = output_file.read_text()
        lines = content.strip().split("\n")
        assert lines[0] == "C,A,B"

    def test_extra_columns_ignored(self, tmp_path):
        """Verify extra columns in records are ignored."""
        output_file = tmp_path / "output.csv"
        records = [{"A": 1, "B": 2, "Extra": "ignored"}]

        write_csv(records, output_file, columns=["A", "B"])

        content = output_file.read_text()
        assert "Extra" not in content


class TestWriteExcel:
    """Tests for write_excel function."""

    def test_basic_write(self, tmp_path):
        """Verify basic Excel writing."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        output_file = tmp_path / "output.xlsx"
        records = [
            {"LPN_ID": "123", "Name": "Ram A"},
            {"LPN_ID": "456", "Name": "Ewe B"},
        ]

        write_excel(records, output_file)

        assert output_file.exists()
        df = pd.read_excel(output_file)
        assert len(df) == 2
        # Note: pandas may read numeric strings as integers
        assert str(df["LPN_ID"].iloc[0]) == "123"

    def test_custom_sheet_name(self, tmp_path):
        """Verify custom sheet name is used."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        output_file = tmp_path / "output.xlsx"
        records = [{"LPN_ID": "123"}]

        write_excel(records, output_file, sheet_name="Flock")

        xl = pd.ExcelFile(output_file)
        assert "Flock" in xl.sheet_names

    def test_empty_records(self, tmp_path):
        """Verify empty records produces no file write."""
        pytest.importorskip("openpyxl")
        output_file = tmp_path / "empty.xlsx"

        write_excel([], output_file)

        assert not output_file.exists()

    def test_custom_column_order(self, tmp_path):
        """Verify custom column order is respected."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        output_file = tmp_path / "output.xlsx"
        records = [{"A": 1, "B": 2, "C": 3}]

        write_excel(records, output_file, columns=["C", "A", "B"])

        df = pd.read_excel(output_file)
        assert list(df.columns) == ["C", "A", "B"]

    def test_import_error_without_pandas(self, tmp_path):
        """Verify ImportError when pandas not available."""
        with patch.dict("sys.modules", {"pandas": None}):
            with patch("builtins.__import__", side_effect=ImportError("No pandas")):
                with pytest.raises(ImportError) as exc_info:
                    write_excel([{"a": 1}], tmp_path / "test.xlsx")
                assert "pandas" in str(exc_info.value)


class TestWriteSpreadsheet:
    """Tests for write_spreadsheet function."""

    def test_auto_detect_csv(self, tmp_path):
        """Verify CSV format detected from .csv extension."""
        output_file = tmp_path / "output.csv"
        records = [{"A": 1}]

        write_spreadsheet(records, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "A" in content

    def test_auto_detect_excel(self, tmp_path):
        """Verify Excel format detected from .xlsx extension."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        output_file = tmp_path / "output.xlsx"
        records = [{"A": 1}]

        write_spreadsheet(records, output_file)

        assert output_file.exists()
        df = pd.read_excel(output_file)
        assert len(df) == 1

    def test_explicit_csv_format(self, tmp_path):
        """Verify explicit CSV format override."""
        output_file = tmp_path / "output.xlsx"  # Wrong extension
        records = [{"A": 1}]

        write_spreadsheet(records, output_file, format="csv")

        content = output_file.read_text()
        assert "A" in content

    def test_explicit_excel_format(self, tmp_path):
        """Verify explicit Excel format override."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        output_file = tmp_path / "output.csv"  # Wrong extension
        records = [{"A": 1}]

        write_spreadsheet(records, output_file, format="excel")

        df = pd.read_excel(output_file)
        assert len(df) == 1

    def test_sheet_name_passed(self, tmp_path):
        """Verify sheet_name is passed to Excel writer."""
        pytest.importorskip("openpyxl")
        import pandas as pd

        output_file = tmp_path / "output.xlsx"
        records = [{"A": 1}]

        write_spreadsheet(records, output_file, sheet_name="Custom")

        xl = pd.ExcelFile(output_file)
        assert "Custom" in xl.sheet_names

    def test_columns_passed(self, tmp_path):
        """Verify columns parameter is passed through."""
        output_file = tmp_path / "output.csv"
        records = [{"A": 1, "B": 2}]

        write_spreadsheet(records, output_file, columns=["B", "A"])

        lines = output_file.read_text().strip().split("\n")
        assert lines[0] == "B,A"

    def test_xls_detected_as_excel(self, tmp_path):
        """Verify .xls extension detected as Excel format."""
        pytest.importorskip("openpyxl")

        output_file = tmp_path / "output.xls"
        records = [{"A": 1}]

        write_spreadsheet(records, output_file)

        # File should exist (will be xlsx format internally)
        assert output_file.exists()
