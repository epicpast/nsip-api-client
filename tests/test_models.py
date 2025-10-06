"""
Tests for data models
"""

import pytest
from nsip_client.models import (
    SearchCriteria,
    AnimalDetails,
    Progeny,
    ProgenyAnimal,
    Trait,
    ContactInfo,
    SearchResults,
)


class TestSearchCriteria:
    """Test SearchCriteria model"""

    def test_empty_criteria(self):
        """Test creating empty criteria"""
        criteria = SearchCriteria()
        assert criteria.to_dict() == {}

    def test_full_criteria(self):
        """Test creating criteria with all fields"""
        criteria = SearchCriteria(
            breed_group_id=64,
            breed_id=486,
            born_after="2020-01-01",
            born_before="2020-12-31",
            gender="Female",
            proven_only=True,
            status="CURRENT",
            flock_id="ABC123",
            trait_ranges={"BWT": {"min": 0.0, "max": 1.0}},
        )
        data = criteria.to_dict()
        assert data["breedGroupId"] == 64
        assert data["breedId"] == 486
        assert data["gender"] == "Female"
        assert data["provenOnly"] is True


class TestAnimalDetails:
    """Test AnimalDetails model"""

    @pytest.fixture
    def mock_api_response(self):
        """Mock API response"""
        return {
            "LpnId": "6####92020###249",
            "Breed": "Katahdin",
            "BreedGroup": "Hair",
            "DateOfBirth": "2/5/2020",
            "Gender": "Female",
            "Status": "CURRENT",
            "Sire": "6####92019###124",
            "Dam": "6####92018###035",
            "RegistrationNumber": "REG123",
            "TotalProgeny": 6,
            "FlockCount": 1,
            "Genotyped": "No",
            "Traits": {
                "BWT": {"Value": 0.246, "Accuracy": 74},
                "WWT": {"Value": 3.051, "Accuracy": 71},
                "NLB": {"Value": 0.119, "Accuracy": 57},
            },
            "ContactInfo": {
                "FarmName": "[FARM_NAME]",
                "ContactName": "[OWNER_NAME]",
                "Phone": "[PHONE_NUMBER]",
                "Email": "[EMAIL_ADDRESS]",
                "Address": "15424 Blessed Ln",
                "City": "Abingdon",
                "State": "VA",
                "ZipCode": "24210",
            },
        }

    def test_from_api_response(self, mock_api_response):
        """Test creating AnimalDetails from API response"""
        animal = AnimalDetails.from_api_response(mock_api_response)

        assert animal.lpn_id == "6####92020###249"
        assert animal.breed == "Katahdin"
        assert animal.breed_group == "Hair"
        assert animal.gender == "Female"
        assert animal.status == "CURRENT"
        assert animal.total_progeny == 6
        assert animal.genotyped == "No"

    def test_traits_parsing(self, mock_api_response):
        """Test trait parsing"""
        animal = AnimalDetails.from_api_response(mock_api_response)

        assert "BWT" in animal.traits
        assert animal.traits["BWT"].value == 0.246
        assert animal.traits["BWT"].accuracy == 74
        assert animal.traits["WWT"].value == 3.051
        assert "NLB" in animal.traits

    def test_contact_info_parsing(self, mock_api_response):
        """Test contact info parsing"""
        animal = AnimalDetails.from_api_response(mock_api_response)

        assert animal.contact_info is not None
        assert animal.contact_info.farm_name == "[FARM_NAME]"
        assert animal.contact_info.phone == "[PHONE_NUMBER]"
        assert animal.contact_info.email == "[EMAIL_ADDRESS]"
        assert animal.contact_info.city == "Abingdon"
        assert animal.contact_info.state == "VA"

    def test_minimal_response(self):
        """Test with minimal API response"""
        minimal_data = {"LpnId": "TEST123"}
        animal = AnimalDetails.from_api_response(minimal_data)

        assert animal.lpn_id == "TEST123"
        assert animal.breed is None
        assert animal.traits == {}
        assert animal.contact_info is None


class TestProgeny:
    """Test Progeny model"""

    @pytest.fixture
    def mock_progeny_response(self):
        """Mock progeny API response"""
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

    def test_from_api_response(self, mock_progeny_response):
        """Test creating Progeny from API response"""
        progeny = Progeny.from_api_response(mock_progeny_response)

        assert progeny.total_count == 6
        assert progeny.page == 0
        assert progeny.page_size == 10
        assert len(progeny.animals) == 2

    def test_progeny_animals(self, mock_progeny_response):
        """Test progeny animals parsing"""
        progeny = Progeny.from_api_response(mock_progeny_response)

        first = progeny.animals[0]
        assert first.lpn_id == "6401492022FLE059"
        assert first.sex == "F"
        assert first.date_of_birth == "02/17/2022"
        assert first.traits["BWT"] == 0.378

        second = progeny.animals[1]
        assert second.lpn_id == "6401492022FLE380"
        assert second.sex == "M"

    def test_empty_progeny(self):
        """Test with no progeny"""
        data = {"TotalCount": 0, "Results": []}
        progeny = Progeny.from_api_response(data)

        assert progeny.total_count == 0
        assert len(progeny.animals) == 0


class TestSearchResults:
    """Test SearchResults model"""

    def test_from_api_response(self):
        """Test creating SearchResults from API response"""
        data = {
            "TotalCount": 100,
            "Page": 2,
            "PageSize": 15,
            "Results": [
                {"LpnId": "ANIMAL1"},
                {"LpnId": "ANIMAL2"},
            ],
        }
        results = SearchResults.from_api_response(data)

        assert results.total_count == 100
        assert results.page == 2
        assert results.page_size == 15
        assert len(results.results) == 2

    def test_empty_results(self):
        """Test with no results"""
        data = {"TotalCount": 0, "Results": []}
        results = SearchResults.from_api_response(data)

        assert results.total_count == 0
        assert len(results.results) == 0
