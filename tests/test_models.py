"""
Tests for data models
"""

import pytest

from nsip_client.models import (
    AnimalDetails,
    Progeny,
    SearchCriteria,
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
    def mock_api_response_legacy(self):
        """Mock API response in legacy format (PascalCase at root)"""
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

    @pytest.fixture
    def mock_api_response_nested(self):
        """Mock API response in new nested format"""
        return {
            "success": True,
            "data": {
                "progenyCount": 25,
                "dateOfBirth": "2/13/2024",
                "gender": "Male",
                "genotyped": "50K Genotyped",
                "flockCount": "1",
                "breed": {
                    "breedName": "Katahdin",
                    "breedDisplayString": "640 - Katahdin",
                    "breedId": 640,
                },
                "searchResultViewModel": {
                    "lpnId": "6402382024NCS310",
                    "lpnSre": "6400462020VPI007",
                    "lpnDam": "6402382022NCS087",
                    "status": "CURRENT",
                    "regNumber": "",
                    "bwt": -0.227,
                    "accbwt": 0.80,
                    "wwt": -0.628,
                    "accwwt": 0.75,
                    "pwwt": -0.352,
                    "accpwwt": 0.72,
                    "ywt": -1.145,
                    "accywt": 0.70,
                    "nlb": 0.059,
                    "accnlb": 0.65,
                },
                "contactInfo": {
                    "flockCode": "640238",
                    "farmName": "North Carolina State University Katahdins",
                    "customerName": "Andrew Weaver",
                    "phone": "555-1234",
                    "email": "test@example.com",
                    "city": "Raleigh",
                    "state": "NC",
                },
            },
        }

    def test_from_api_response_legacy(self, mock_api_response_legacy):
        """Test creating AnimalDetails from legacy API response"""
        animal = AnimalDetails.from_api_response(mock_api_response_legacy)

        assert animal.lpn_id == "6####92020###249"
        assert animal.breed == "Katahdin"
        assert animal.breed_group == "Hair"
        assert animal.gender == "Female"
        assert animal.status == "CURRENT"
        assert animal.total_progeny == 6
        assert animal.genotyped == "No"

    def test_from_api_response_nested(self, mock_api_response_nested):
        """Test creating AnimalDetails from new nested API response"""
        animal = AnimalDetails.from_api_response(mock_api_response_nested)

        assert animal.lpn_id == "6402382024NCS310"
        assert animal.breed == "Katahdin"
        assert animal.status == "CURRENT"
        assert animal.total_progeny == 25
        assert animal.sire == "6400462020VPI007"
        assert animal.dam == "6402382022NCS087"
        assert animal.gender == "Male"
        assert animal.genotyped == "50K Genotyped"
        assert animal.flock_count == 1

    def test_traits_parsing_legacy(self, mock_api_response_legacy):
        """Test trait parsing from legacy format"""
        animal = AnimalDetails.from_api_response(mock_api_response_legacy)

        assert "BWT" in animal.traits
        assert animal.traits["BWT"].value == 0.246
        assert animal.traits["BWT"].accuracy == 74
        assert animal.traits["WWT"].value == 3.051
        assert "NLB" in animal.traits

    def test_traits_parsing_nested(self, mock_api_response_nested):
        """Test trait parsing from nested format"""
        animal = AnimalDetails.from_api_response(mock_api_response_nested)

        assert len(animal.traits) > 0
        assert "BWT" in animal.traits
        assert animal.traits["BWT"].value == -0.227
        # Accuracy should be converted from 0.80 to 80
        assert animal.traits["BWT"].accuracy == 80
        assert "WWT" in animal.traits
        assert animal.traits["WWT"].value == -0.628
        assert animal.traits["WWT"].accuracy == 75
        assert "NLB" in animal.traits

    def test_contact_info_parsing_legacy(self, mock_api_response_legacy):
        """Test contact info parsing from legacy format"""
        animal = AnimalDetails.from_api_response(mock_api_response_legacy)

        assert animal.contact_info is not None
        assert animal.contact_info.farm_name == "[FARM_NAME]"
        assert animal.contact_info.phone == "[PHONE_NUMBER]"
        assert animal.contact_info.email == "[EMAIL_ADDRESS]"
        assert animal.contact_info.city == "Abingdon"
        assert animal.contact_info.state == "VA"

    def test_contact_info_parsing_nested(self, mock_api_response_nested):
        """Test contact info parsing from nested format"""
        animal = AnimalDetails.from_api_response(mock_api_response_nested)

        assert animal.contact_info is not None
        assert animal.contact_info.farm_name == "North Carolina State University Katahdins"
        assert animal.contact_info.contact_name == "Andrew Weaver"
        assert animal.contact_info.phone == "555-1234"
        assert animal.contact_info.email == "test@example.com"
        assert animal.contact_info.city == "Raleigh"
        assert animal.contact_info.state == "NC"

    def test_minimal_response(self):
        """Test with minimal API response"""
        minimal_data = {"LpnId": "TEST123"}
        animal = AnimalDetails.from_api_response(minimal_data)

        assert animal.lpn_id == "TEST123"
        assert animal.breed is None
        assert animal.traits == {}
        assert animal.contact_info is None

    def test_minimal_nested_response(self):
        """Test with minimal nested API response"""
        minimal_data = {
            "success": True,
            "data": {"searchResultViewModel": {"lpnId": "TEST456"}},
        }
        animal = AnimalDetails.from_api_response(minimal_data)

        assert animal.lpn_id == "TEST456"
        assert animal.breed is None
        assert animal.traits == {}


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
