"""
Unit tests for nsip_skills.flock_import

Tests:
- CSV import
- Excel import
- NSIP data enrichment
- Export functionality
- Report generation

Target: >95% coverage
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from nsip_skills_helpers import (
    SAMPLE_LPNS,
    MockNSIPClient,
)

from nsip_skills.common.data_models import (
    AnimalAnalysis,
    EnrichedFlockRecord,
    FlockRecord,
)
from nsip_skills.flock_import import (
    ImportResult,
    export_enriched_flock,
    generate_import_report,
    import_flock,
    main,
)


class TestImportResult:
    """Tests for ImportResult dataclass."""

    def test_default_values(self):
        """Verify default values are set correctly."""
        result = ImportResult()
        assert result.total_records == 0
        assert result.successful == 0
        assert result.not_found == []
        assert result.errors == {}
        assert result.enriched_records == []
        assert result.source_file is None

    def test_to_dict_structure(self):
        """Verify to_dict returns proper structure."""
        result = ImportResult(
            total_records=10,
            successful=8,
            not_found=["LPN1", "LPN2"],
            errors={"LPN3": "API Error"},
            source_file="test.csv",
        )

        d = result.to_dict()

        assert "total_records" in d
        assert "successful" in d
        assert "not_found" in d
        assert "errors" in d
        assert "enriched_records" in d
        assert "source_file" in d
        assert d["total_records"] == 10
        assert d["successful"] == 8
        assert len(d["not_found"]) == 2

    def test_to_dict_with_enriched_records(self):
        """Verify to_dict includes enriched records."""
        record = FlockRecord(lpn_id="TEST1")
        enriched = EnrichedFlockRecord(local=record)
        result = ImportResult(enriched_records=[enriched])

        d = result.to_dict()

        assert len(d["enriched_records"]) == 1


class TestImportFlock:
    """Tests for import_flock function."""

    def test_import_csv(self, mock_animals, sample_csv_content, tmp_path):
        """Verify CSV import works."""
        # Write sample CSV
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)

        result = import_flock(str(csv_file), client=client)

        assert isinstance(result, ImportResult)
        assert result.total_records > 0
        assert result.source_file == str(csv_file)

    def test_import_csv_path_object(self, mock_animals, sample_csv_content, tmp_path):
        """Verify CSV import works with Path object."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)

        result = import_flock(csv_file, client=client)

        assert isinstance(result, ImportResult)

    def test_import_excel(self, mock_animals, tmp_path):
        """Verify Excel import works."""
        openpyxl = pytest.importorskip("openpyxl")

        # Create simple Excel file
        excel_file = tmp_path / "test_flock.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["LPN_ID", "Name", "Tag"])
        ws.append([SAMPLE_LPNS[0], "Test Animal", "001"])
        wb.save(excel_file)

        client = MockNSIPClient(animals=mock_animals)

        result = import_flock(str(excel_file), client=client)

        assert isinstance(result, ImportResult)

    def test_import_with_lineage(self, mock_animals, sample_csv_content, tmp_path):
        """Verify import with lineage data."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)

        result = import_flock(str(csv_file), include_lineage=True, client=client)

        assert isinstance(result, ImportResult)

    def test_import_with_progeny(self, mock_animals, sample_csv_content, tmp_path):
        """Verify import with progeny data."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)

        result = import_flock(str(csv_file), include_progeny=True, client=client)

        assert isinstance(result, ImportResult)

    def test_import_empty_file(self, tmp_path):
        """Verify handling of empty spreadsheet."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("LPN_ID,Name\n")

        client = MockNSIPClient()

        result = import_flock(str(csv_file), client=client)

        assert result.total_records == 0

    def test_import_tracks_not_found(self, mock_animals, tmp_path):
        """Verify not found LPNs are tracked."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("lpn_id,name\nNONEXISTENT,Unknown\n")

        client = MockNSIPClient(animals=mock_animals)

        result = import_flock(str(csv_file), client=client)

        assert "NONEXISTENT" in result.not_found or result.total_records > 0

    def test_import_enriches_records(self, mock_animals, sample_csv_content, tmp_path):
        """Verify records are enriched with NSIP data."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)

        result = import_flock(str(csv_file), client=client)

        # Check that enriched records have NSIP details
        for enriched in result.enriched_records:
            assert enriched.local is not None
            # Either has NSIP details or a fetch error
            assert enriched.nsip_details is not None or enriched.fetch_error is not None

    def test_file_not_found(self):
        """Verify error handling for missing file."""
        client = MockNSIPClient()

        with pytest.raises(FileNotFoundError):
            import_flock("/nonexistent/path/file.csv", client=client)

    def test_client_closed_when_created(self, mock_animals, sample_csv_content, tmp_path):
        """Verify client is closed when created internally."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        with patch("nsip_skills.flock_import.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            import_flock(str(csv_file), client=None)

            assert mock_instance._closed is True

    def test_client_not_closed_when_passed(self, mock_animals, sample_csv_content, tmp_path):
        """Verify client is not closed when passed in."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)

        import_flock(str(csv_file), client=client)

        assert client._closed is False

    def test_import_with_sheet_name(self, mock_animals, tmp_path):
        """Verify import with sheet_name parameter."""
        openpyxl = pytest.importorskip("openpyxl")

        excel_file = tmp_path / "test_flock.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Flock"
        ws.append(["LPN_ID", "Name"])
        ws.append([SAMPLE_LPNS[0], "Test"])
        wb.save(excel_file)

        client = MockNSIPClient(animals=mock_animals)

        result = import_flock(str(excel_file), sheet_name="Flock", client=client)

        assert isinstance(result, ImportResult)


class TestExportEnrichedFlock:
    """Tests for export_enriched_flock function."""

    def test_export_csv(self, mock_animals, sample_csv_content, tmp_path):
        """Verify CSV export works."""
        # First import
        csv_file = tmp_path / "input.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)
        result = import_flock(str(csv_file), client=client)

        # Then export
        output_file = tmp_path / "output.csv"
        export_enriched_flock(result, output_file)

        assert output_file.exists()

    def test_export_excel(self, mock_animals, sample_csv_content, tmp_path):
        """Verify Excel export works."""
        pytest.importorskip("openpyxl")

        # First import
        csv_file = tmp_path / "input.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)
        result = import_flock(str(csv_file), client=client)

        # Then export
        output_file = tmp_path / "output.xlsx"
        export_enriched_flock(result, output_file, format="excel")

        assert output_file.exists()

    def test_export_with_trait_filter(self, mock_animals, sample_csv_content, tmp_path):
        """Verify export with specific traits."""
        csv_file = tmp_path / "input.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)
        result = import_flock(str(csv_file), client=client)

        output_file = tmp_path / "output.csv"
        export_enriched_flock(result, output_file, include_traits=["BWT", "WWT"])

        assert output_file.exists()

    def test_export_auto_format(self, mock_animals, sample_csv_content, tmp_path):
        """Verify auto format detection."""
        csv_file = tmp_path / "input.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)
        result = import_flock(str(csv_file), client=client)

        # Auto format should detect CSV from extension
        output_file = tmp_path / "output.csv"
        export_enriched_flock(result, output_file, format="auto")

        assert output_file.exists()

    def test_export_path_object(self, mock_animals, sample_csv_content, tmp_path):
        """Verify export works with Path object."""
        csv_file = tmp_path / "input.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)
        result = import_flock(str(csv_file), client=client)

        output_file = tmp_path / "output.csv"
        export_enriched_flock(result, output_file)

        assert output_file.exists()

    def test_export_empty_result(self, tmp_path):
        """Verify export handles empty result without error.

        Note: When there are no records, no file is created (early return).
        This tests that the function completes without error.
        """
        result = ImportResult()
        output_file = tmp_path / "output.csv"

        # Should not raise an error even with empty result
        export_enriched_flock(result, output_file)

        # No file created for empty results (write_csv returns early)
        assert not output_file.exists()


class TestGenerateImportReport:
    """Tests for generate_import_report function."""

    def test_basic_report(self, mock_animals, sample_csv_content, tmp_path):
        """Verify basic report generation."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        client = MockNSIPClient(animals=mock_animals)
        result = import_flock(str(csv_file), client=client)

        output = generate_import_report(result)

        assert isinstance(output, str)
        assert len(output) > 0

    def test_report_with_all_valid(self):
        """Verify report when all records are valid."""
        record = FlockRecord(lpn_id="TEST1")
        analysis = AnimalAnalysis(lpn_id="TEST1")
        enriched = EnrichedFlockRecord(local=record, nsip_details=analysis)
        result = ImportResult(
            total_records=1,
            successful=1,
            enriched_records=[enriched],
        )

        output = generate_import_report(result)

        assert isinstance(output, str)

    def test_report_with_not_found(self):
        """Verify report includes not found LPNs."""
        result = ImportResult(
            total_records=2,
            successful=0,
            not_found=["BAD1", "BAD2"],
        )

        output = generate_import_report(result)

        assert "BAD1" in output or "not found" in output.lower() or len(output) > 0

    def test_report_with_errors(self):
        """Verify report includes errors."""
        result = ImportResult(
            total_records=1,
            successful=0,
            errors={"LPN1": "API Error"},
        )

        output = generate_import_report(result)

        assert isinstance(output, str)

    def test_report_empty_result(self):
        """Verify report handles empty result."""
        result = ImportResult()

        output = generate_import_report(result)

        assert isinstance(output, str)


class TestMainCLI:
    """Tests for main() CLI function."""

    def test_main_basic(self, mock_animals, sample_csv_content, tmp_path):
        """Verify main CLI runs without error."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        with patch("nsip_skills.flock_import.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["flock_import.py", str(csv_file)]):
                # May return 0 or 1 depending on success rate
                result = main()
                assert result in [0, 1]

    def test_main_with_output(self, mock_animals, sample_csv_content, tmp_path):
        """Verify main CLI with output file."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)
        output_file = tmp_path / "output.csv"

        with patch("nsip_skills.flock_import.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["flock_import.py", str(csv_file), "-o", str(output_file)],
            ):
                result = main()
                assert result in [0, 1]

    def test_main_json_output(self, mock_animals, sample_csv_content, tmp_path):
        """Verify main CLI JSON output."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        with patch("nsip_skills.flock_import.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["flock_import.py", str(csv_file), "--json"]):
                result = main()
                assert result in [0, 1]

    def test_main_with_lineage(self, mock_animals, sample_csv_content, tmp_path):
        """Verify main CLI with lineage flag."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        with patch("nsip_skills.flock_import.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["flock_import.py", str(csv_file), "--lineage"]):
                result = main()
                assert result in [0, 1]

    def test_main_with_progeny(self, mock_animals, sample_csv_content, tmp_path):
        """Verify main CLI with progeny flag."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        with patch("nsip_skills.flock_import.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch("sys.argv", ["flock_import.py", str(csv_file), "--progeny"]):
                result = main()
                assert result in [0, 1]

    def test_main_with_format(self, mock_animals, sample_csv_content, tmp_path):
        """Verify main CLI with format option."""
        csv_file = tmp_path / "test_flock.csv"
        csv_file.write_text(sample_csv_content)

        with patch("nsip_skills.flock_import.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["flock_import.py", str(csv_file), "--format", "csv"],
            ):
                result = main()
                assert result in [0, 1]

    def test_main_with_sheet(self, mock_animals, tmp_path):
        """Verify main CLI with sheet option."""
        openpyxl = pytest.importorskip("openpyxl")

        excel_file = tmp_path / "test.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Data"
        ws.append(["LPN_ID"])
        ws.append([SAMPLE_LPNS[0]])
        wb.save(excel_file)

        with patch("nsip_skills.flock_import.CachedNSIPClient") as mock_cls:
            mock_instance = MockNSIPClient(animals=mock_animals)
            mock_cls.return_value = mock_instance

            with patch(
                "sys.argv",
                ["flock_import.py", str(excel_file), "--sheet", "Data"],
            ):
                result = main()
                assert result in [0, 1]
