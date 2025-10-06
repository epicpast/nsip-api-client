"""
Tests for the NSIP API client
"""

import pytest
import requests_mock
from nsip_client import NSIPClient
from nsip_client.exceptions import (
    NSIPAPIError,
    NSIPNotFoundError,
    NSIPTimeoutError,
    NSIPValidationError,
)
from nsip_client.models import AnimalDetails, Progeny, SearchResults


class TestNSIPClient:
    """Test suite for NSIPClient"""

    @pytest.fixture
    def client(self):
        """Create a test client instance"""
        return NSIPClient(timeout=10)

    @pytest.fixture
    def mock_animal_details(self):
        """Mock animal details response"""
        return {
            "LpnId": "6####92020###249",
            "Breed": "Katahdin",
            "BreedGroup": "Hair",
            "DateOfBirth": "2/5/2020",
            "Gender": "Female",
            "Status": "CURRENT",
            "Sire": "6####92019###124",
            "Dam": "6####92018###035",
            "TotalProgeny": 6,
            "Genotyped": "No",
            "Traits": {
                "BWT": {"Value": 0.246, "Accuracy": 74},
                "WWT": {"Value": 3.051, "Accuracy": 71},
            },
            "ContactInfo": {
                "FarmName": "[FARM_NAME]",
                "Phone": "[PHONE_NUMBER]",
                "Email": "[EMAIL_ADDRESS]",
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
    def mock_search_results(self):
        """Mock search results response"""
        return {
            "TotalCount": 100,
            "Page": 0,
            "PageSize": 15,
            "Results": [
                {"LpnId": "4860011995NFA84J", "BWT": 0, "WWT": 0},
                {"LpnId": "4860011996KSB264", "BWT": 0, "WWT": 0},
            ],
        }

    def test_client_initialization(self, client):
        """Test client initializes correctly"""
        assert client.timeout == 10
        assert client.base_url == "http://nsipsearch.nsip.org/api"
        assert "Accept" in client.session.headers

    def test_context_manager(self):
        """Test client works as context manager"""
        with NSIPClient() as client:
            assert client is not None
        # Session should be closed after exiting context

    def test_get_date_last_updated(self, client):
        """Test getting last update date"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/search/getDateLastUpdated",
                json={"date": "09/23/2025"},
            )
            result = client.get_date_last_updated()
            assert result["date"] == "09/23/2025"

    def test_get_available_breed_groups(self, client, mock_breed_groups):
        """Test getting breed groups"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/search/getAvailableBreedGroups",
                json=mock_breed_groups,
            )
            groups = client.get_available_breed_groups()
            assert len(groups) == 4
            assert groups[0].id == 61
            assert groups[0].name == "Range"

    def test_get_animal_details(self, client, mock_animal_details):
        """Test getting animal details"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/details/getAnimalDetails",
                json=mock_animal_details,
            )
            animal = client.get_animal_details("6####92020###249")
            assert isinstance(animal, AnimalDetails)
            assert animal.lpn_id == "6####92020###249"
            assert animal.breed == "Katahdin"
            assert animal.gender == "Female"
            assert "BWT" in animal.traits
            assert animal.traits["BWT"].value == 0.246

    def test_get_animal_details_not_found(self, client):
        """Test handling of animal not found"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/details/getAnimalDetails",
                status_code=404,
            )
            with pytest.raises(NSIPNotFoundError):
                client.get_animal_details("INVALID123")

    def test_get_animal_details_validation(self, client):
        """Test validation of search string"""
        with pytest.raises(NSIPValidationError):
            client.get_animal_details("")

        with pytest.raises(NSIPValidationError):
            client.get_animal_details("   ")

    def test_get_progeny(self, client, mock_progeny):
        """Test getting progeny"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/details/getPageOfProgeny",
                json=mock_progeny,
            )
            progeny = client.get_progeny("6####92020###249")
            assert isinstance(progeny, Progeny)
            assert progeny.total_count == 6
            assert len(progeny.animals) == 2
            assert progeny.animals[0].lpn_id == "6401492022FLE059"
            assert progeny.animals[0].sex == "F"

    def test_get_progeny_validation(self, client):
        """Test progeny parameter validation"""
        with pytest.raises(NSIPValidationError):
            client.get_progeny("")

        with pytest.raises(NSIPValidationError):
            client.get_progeny("123", page=-1)

        with pytest.raises(NSIPValidationError):
            client.get_progeny("123", page_size=0)

    def test_search_animals(self, client, mock_search_results):
        """Test searching for animals"""
        with requests_mock.Mocker() as m:
            m.post(
                "http://nsipsearch.nsip.org/api/search/getPageOfSearchResults",
                json=mock_search_results,
            )
            results = client.search_animals(breed_id=486, page_size=15)
            assert isinstance(results, SearchResults)
            assert results.total_count == 100
            assert len(results.results) == 2

    def test_search_animals_validation(self, client):
        """Test search parameter validation"""
        with pytest.raises(NSIPValidationError):
            client.search_animals(page=-1)

        with pytest.raises(NSIPValidationError):
            client.search_animals(page_size=0)

        with pytest.raises(NSIPValidationError):
            client.search_animals(page_size=101)

    def test_get_trait_ranges_validation(self, client):
        """Test trait ranges parameter validation"""
        with pytest.raises(NSIPValidationError):
            client.get_trait_ranges_by_breed(-1)

        with pytest.raises(NSIPValidationError):
            client.get_trait_ranges_by_breed(0)

        with pytest.raises(NSIPValidationError):
            client.get_trait_ranges_by_breed("invalid")

    def test_timeout_error(self, client):
        """Test timeout handling"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/search/getDateLastUpdated",
                exc=requests.exceptions.Timeout,
            )
            with pytest.raises(NSIPTimeoutError):
                client.get_date_last_updated()

    def test_connection_error(self, client):
        """Test connection error handling"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/search/getDateLastUpdated",
                exc=requests.exceptions.ConnectionError,
            )
            with pytest.raises(NSIPAPIError):
                client.get_date_last_updated()

    def test_api_error_with_response(self, client):
        """Test API error with response"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/search/getDateLastUpdated",
                status_code=500,
                text="Internal Server Error",
            )
            with pytest.raises(NSIPAPIError) as exc_info:
                client.get_date_last_updated()
            assert exc_info.value.status_code == 500

    def test_search_by_lpn(self, client, mock_animal_details, mock_progeny):
        """Test convenience method to get full profile"""
        with requests_mock.Mocker() as m:
            m.get(
                "http://nsipsearch.nsip.org/api/details/getAnimalDetails",
                json=mock_animal_details,
            )
            m.get(
                "http://nsipsearch.nsip.org/api/details/getLineage",
                json={"lineage": "data"},
            )
            m.get(
                "http://nsipsearch.nsip.org/api/details/getPageOfProgeny",
                json=mock_progeny,
            )

            profile = client.search_by_lpn("6####92020###249")
            assert "details" in profile
            assert "lineage" in profile
            assert "progeny" in profile
            assert isinstance(profile["details"], AnimalDetails)
            assert isinstance(profile["progeny"], Progeny)
