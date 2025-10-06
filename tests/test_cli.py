"""
Tests for the NSIP CLI module
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests_mock

from nsip_client import __version__
from nsip_client.cli import main


class TestCLI:
    """Test suite for CLI commands"""

    @pytest.fixture
    def mock_animal_details(self):
        """Mock animal details response"""
        return {
            "LpnId": "6401492020FLE249",
            "Breed": "Katahdin",
            "BreedGroup": "Hair",
            "DateOfBirth": "2/5/2020",
            "Gender": "Female",
            "Status": "CURRENT",
            "Sire": "6401492019FLE124",
            "Dam": "6401492018FLE035",
            "TotalProgeny": 6,
            "Genotyped": "No",
            "Traits": {
                "BWT": {"Value": 0.246, "Accuracy": 74},
                "WWT": {"Value": 3.051, "Accuracy": 71},
            },
            "ContactInfo": {
                "FarmName": "Beyond Blessed Farm",
                "Phone": "(276)-759-4718",
                "Email": "mbfletcher08@gmail.com",
            },
        }

    @pytest.fixture
    def mock_breed_groups(self):
        """Mock breed groups response"""
        return [
            {"Id": 61, "Name": "Range"},
            {"Id": 62, "Name": "Maternal Wool"},
            {"Id": 64, "Name": "Hair"},
            {"Id": 69, "Name": "Terminal"},
        ]

    @pytest.fixture
    def mock_progeny(self):
        """Mock progeny response"""
        return {
            "TotalCount": 6,
            "Page": 0,
            "PageSize": 10,
            "Results": [
                {
                    "LpnId": "6401492022FLE059",
                    "Sex": "F",
                    "DateOfBirth": "02/17/2022",
                    "Traits": {"BWT": 0.378, "WWT": 3.141},
                },
                {
                    "LpnId": "6401492022FLE380",
                    "Sex": "M",
                    "DateOfBirth": "02/17/2022",
                    "Traits": {"BWT": 0.607, "WWT": 3.848},
                },
            ],
        }

    @pytest.fixture
    def mock_lineage(self):
        """Mock lineage response"""
        return {
            "Subject": {"LpnId": "6401492020FLE249", "FarmName": "Beyond Blessed Farm"},
            "Sire": {"LpnId": "6401492019FLE124"},
            "Dam": {"LpnId": "6401492018FLE035"},
        }

    @pytest.fixture
    def mock_search_results(self):
        """Mock search results response"""
        return {
            "TotalCount": 100,
            "Page": 0,
            "PageSize": 15,
            "Results": [
                {"LpnId": "4860011995NFA84J", "BWT": 0, "WWT": 0},
                {"LpnId": "4860011996KSB264", "BWT": 0, "WWT": 0},
                {"LpnId": "4860011997ABC123", "BWT": 0.5, "WWT": 1.2},
            ],
        }

    def test_version_flag(self, capsys):
        """Test --version flag"""
        exit_code = main(["--version"])
        captured = capsys.readouterr()
        assert exit_code == 0
        assert __version__ in captured.out
        assert "nsip-client version" in captured.out

    def test_no_command_prints_help(self, capsys):
        """Test that running with no command prints help"""
        exit_code = main([])
        captured = capsys.readouterr()
        assert exit_code == 1
        assert "NSIP Search API Command Line Interface" in captured.out

    def test_search_command_simple(self, mock_animal_details, capsys):
        """Test simple search command without --full flag"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/details/getAnimalDetails",
                json=mock_animal_details,
            )

            exit_code = main(["search", "6401492020FLE249"])
            captured = capsys.readouterr()

            assert exit_code == 0
            output = json.loads(captured.out)
            assert output["LpnId"] == "6401492020FLE249"
            assert output["Breed"] == "Katahdin"

    def test_search_command_full(self, mock_animal_details, mock_lineage, mock_progeny, capsys):
        """Test search command with --full flag"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/details/getAnimalDetails",
                json=mock_animal_details,
            )
            m.get(
                "http://nsipsearch.nsip.org/api/details/getLineage",
                json=mock_lineage,
            )
            m.get(
                "http://nsipsearch.nsip.org/api/details/getPageOfProgeny",
                json=mock_progeny,
            )

            exit_code = main(["search", "6401492020FLE249", "--full"])
            captured = capsys.readouterr()

            assert exit_code == 0
            output = json.loads(captured.out)
            assert "details" in output
            assert "lineage" in output
            assert "progeny" in output
            assert output["details"]["LpnId"] == "6401492020FLE249"
            assert output["progeny"]["total_count"] == 6
            assert len(output["progeny"]["animals"]) == 2
            assert output["progeny"]["animals"][0]["lpn_id"] == "6401492022FLE059"

    def test_breeds_command(self, mock_breed_groups, capsys):
        """Test breeds command"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/search/getAvailableBreedGroups",
                json=mock_breed_groups,
            )

            exit_code = main(["breeds"])
            captured = capsys.readouterr()

            assert exit_code == 0
            assert "61: Range" in captured.out
            assert "62: Maternal Wool" in captured.out
            assert "64: Hair" in captured.out
            assert "69: Terminal" in captured.out

    def test_find_command_basic(self, mock_search_results, capsys):
        """Test find command with basic parameters"""
        with requests_mock.Mocker() as m:
            m.post(
                "http://nsipsearch.nsip.org/api/search/getPageOfSearchResults",
                json=mock_search_results,
            )

            exit_code = main(["find"])
            captured = capsys.readouterr()

            assert exit_code == 0
            assert "Total results: 100" in captured.out
            assert "Page 1 (3 results):" in captured.out
            assert "4860011995NFA84J" in captured.out
            assert "4860011996KSB264" in captured.out
            assert "4860011997ABC123" in captured.out

    def test_find_command_with_breed_id(self, mock_search_results, capsys):
        """Test find command with breed ID filter"""
        with requests_mock.Mocker() as m:
            m.post(
                "http://nsipsearch.nsip.org/api/search/getPageOfSearchResults",
                json=mock_search_results,
            )

            exit_code = main(["find", "--breed-id", "486"])
            captured = capsys.readouterr()

            assert exit_code == 0
            assert "Total results: 100" in captured.out

    def test_find_command_with_pagination(self, capsys):
        """Test find command with pagination parameters"""
        # Create a mock result with page 2 (0-indexed)
        paginated_results = {
            "TotalCount": 100,
            "Page": 2,
            "PageSize": 20,
            "Results": [
                {"LpnId": "4860011995NFA84J", "BWT": 0, "WWT": 0},
                {"LpnId": "4860011996KSB264", "BWT": 0, "WWT": 0},
                {"LpnId": "4860011997ABC123", "BWT": 0.5, "WWT": 1.2},
            ],
        }
        with requests_mock.Mocker() as m:
            m.post(
                "http://nsipsearch.nsip.org/api/search/getPageOfSearchResults",
                json=paginated_results,
            )

            exit_code = main(["find", "--page", "2", "--page-size", "20"])
            captured = capsys.readouterr()

            assert exit_code == 0
            assert (
                "Page 3 (3 results):" in captured.out
            )  # Page 2 is 0-indexed, display is 1-indexed

    def test_search_not_found_error(self, capsys):
        """Test handling of animal not found"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/details/getAnimalDetails",
                status_code=404,
            )

            exit_code = main(["search", "INVALID123"])
            captured = capsys.readouterr()

            assert exit_code == 1
            assert "Error:" in captured.err

    def test_nsip_error_handling(self, capsys):
        """Test handling of NSIPError exceptions"""
        with requests_mock.Mocker() as m:
            # Simulate a validation error by making the API return a 400
            m.get(
                "http://nsipsearch.nsip.org/api/details/getAnimalDetails",
                status_code=500,
                text="Internal Server Error",
            )

            exit_code = main(["search", "6401492020FLE249"])
            captured = capsys.readouterr()

            assert exit_code == 1
            assert "Error:" in captured.err

    def test_unexpected_error_handling(self, capsys):
        """Test handling of unexpected exceptions"""
        with patch("nsip_client.cli.NSIPClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            # Raise an unexpected exception
            mock_client.get_animal_details.side_effect = ValueError("Unexpected error")

            exit_code = main(["search", "6401492020FLE249"])
            captured = capsys.readouterr()

            assert exit_code == 2
            assert "Unexpected error:" in captured.err

    def test_find_command_empty_results(self, capsys):
        """Test find command with no LpnId in results"""
        mock_results = {
            "TotalCount": 10,
            "Page": 0,
            "PageSize": 15,
            "Results": [
                {"BWT": 0, "WWT": 0},  # Missing LpnId
                {"LpnId": "TEST123", "BWT": 0.5},
            ],
        }

        with requests_mock.Mocker() as m:
            m.post(
                "http://nsipsearch.nsip.org/api/search/getPageOfSearchResults",
                json=mock_results,
            )

            exit_code = main(["find"])
            captured = capsys.readouterr()

            assert exit_code == 0
            assert "N/A" in captured.out  # Missing LpnId shows as N/A
            assert "TEST123" in captured.out

    def test_main_as_script(self):
        """Test CLI can be invoked as __main__"""
        # This tests the if __name__ == "__main__" block
        # We'll just verify the import doesn't fail
        import nsip_client.cli

        assert hasattr(nsip_client.cli, "main")

    def test_breeds_command_error_handling(self, capsys):
        """Test error handling in breeds command"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/search/getAvailableBreedGroups",
                status_code=500,
                text="Server Error",
            )

            exit_code = main(["breeds"])
            captured = capsys.readouterr()

            assert exit_code == 1
            assert "Error:" in captured.err

    def test_find_command_error_handling(self, capsys):
        """Test error handling in find command"""
        with requests_mock.Mocker() as m:
            m.post(
                "http://nsipsearch.nsip.org/api/search/getPageOfSearchResults",
                exc=Exception("Network error"),
            )

            exit_code = main(["find"])
            captured = capsys.readouterr()

            assert exit_code == 2
            assert "Unexpected error:" in captured.err
