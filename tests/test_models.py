"""
Tests for data models
"""

import pytest

from nsip_client.models import (
    AnimalDetails,
    BreedGroup,
    ContactInfo,
    Lineage,
    LineageAnimal,
    Progeny,
    ProgenyAnimal,
    SearchCriteria,
    SearchResults,
    Trait,
    _parse_lineage_content,
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

    def test_from_api_response_camelcase(self):
        """Test creating SearchResults from camelCase API response"""
        data = {
            "recordCount": 50,
            "page": 1,
            "pageSize": 20,
            "records": [
                {"lpnId": "ANIMAL1"},
                {"lpnId": "ANIMAL2"},
            ],
        }
        results = SearchResults.from_api_response(data)

        assert results.total_count == 50
        assert results.page == 1
        assert results.page_size == 20
        assert len(results.results) == 2


class TestTrait:
    """Test Trait dataclass"""

    def test_basic_creation(self):
        """Test creating a Trait with all fields"""
        trait = Trait(name="BWT", value=0.5, accuracy=75, units="kg")

        assert trait.name == "BWT"
        assert trait.value == 0.5
        assert trait.accuracy == 75
        assert trait.units == "kg"

    def test_minimal_creation(self):
        """Test creating a Trait with minimal fields"""
        trait = Trait(name="WWT", value=2.5)

        assert trait.name == "WWT"
        assert trait.value == 2.5
        assert trait.accuracy is None
        assert trait.units is None

    def test_negative_value(self):
        """Test trait with negative value (common for EBVs)"""
        trait = Trait(name="BWT", value=-0.25, accuracy=80)

        assert trait.value == -0.25


class TestContactInfo:
    """Test ContactInfo dataclass"""

    def test_full_contact(self):
        """Test creating ContactInfo with all fields"""
        contact = ContactInfo(
            farm_name="Happy Sheep Farm",
            contact_name="John Smith",
            phone="555-1234",
            email="john@sheepfarm.com",
            address="123 Farm Road",
            city="Springfield",
            state="IL",
            zip_code="62701",
        )

        assert contact.farm_name == "Happy Sheep Farm"
        assert contact.contact_name == "John Smith"
        assert contact.phone == "555-1234"
        assert contact.email == "john@sheepfarm.com"
        assert contact.address == "123 Farm Road"
        assert contact.city == "Springfield"
        assert contact.state == "IL"
        assert contact.zip_code == "62701"

    def test_minimal_contact(self):
        """Test creating ContactInfo with no fields"""
        contact = ContactInfo()

        assert contact.farm_name is None
        assert contact.contact_name is None
        assert contact.phone is None


class TestLineageAnimal:
    """Test LineageAnimal dataclass"""

    def test_full_creation(self):
        """Test creating LineageAnimal with all fields"""
        animal = LineageAnimal(
            lpn_id="6401492020TEST001",
            farm_name="Test Farm",
            us_index=110.5,
            src_index=105.2,
            date_of_birth="2020-01-15",
            sex="M",
            status="CURRENT",
        )

        assert animal.lpn_id == "6401492020TEST001"
        assert animal.farm_name == "Test Farm"
        assert animal.us_index == 110.5
        assert animal.src_index == 105.2
        assert animal.date_of_birth == "2020-01-15"
        assert animal.sex == "M"
        assert animal.status == "CURRENT"

    def test_minimal_creation(self):
        """Test creating LineageAnimal with only lpn_id"""
        animal = LineageAnimal(lpn_id="TEST123")

        assert animal.lpn_id == "TEST123"
        assert animal.farm_name is None
        assert animal.us_index is None


class TestAnimalDetailsToDict:
    """Test AnimalDetails.to_dict() method"""

    def test_to_dict_basic(self):
        """Test to_dict with basic fields"""
        animal = AnimalDetails(
            lpn_id="TEST123",
            breed="Suffolk",
            gender="Female",
            status="CURRENT",
        )

        result = animal.to_dict()

        assert result["lpn_id"] == "TEST123"
        assert result["breed"] == "Suffolk"
        assert result["gender"] == "Female"
        assert result["status"] == "CURRENT"

    def test_to_dict_with_traits(self):
        """Test to_dict includes traits"""
        animal = AnimalDetails(
            lpn_id="TEST123",
            traits={
                "BWT": Trait(name="BWT", value=0.5, accuracy=75),
                "WWT": Trait(name="WWT", value=2.5, accuracy=80),
            },
        )

        result = animal.to_dict()

        assert "traits" in result
        assert "BWT" in result["traits"]
        assert result["traits"]["BWT"]["value"] == 0.5
        assert result["traits"]["BWT"]["accuracy"] == 75

    def test_to_dict_with_contact(self):
        """Test to_dict includes contact info"""
        animal = AnimalDetails(
            lpn_id="TEST123",
            contact_info=ContactInfo(
                farm_name="Test Farm",
                email="test@example.com",
            ),
        )

        result = animal.to_dict()

        assert "contact_info" in result
        assert result["contact_info"]["farm_name"] == "Test Farm"
        assert result["contact_info"]["email"] == "test@example.com"

    def test_to_dict_preserves_raw_data(self):
        """Test to_dict includes raw_data"""
        raw = {"originalField": "originalValue"}
        animal = AnimalDetails(
            lpn_id="TEST123",
            raw_data=raw,
        )

        result = animal.to_dict()

        assert result["raw_data"] == raw


class TestProgenyAnimal:
    """Test ProgenyAnimal model"""

    def test_basic_creation(self):
        """Test creating ProgenyAnimal"""
        animal = ProgenyAnimal(
            lpn_id="6401492022FLE059",
            sex="F",
            date_of_birth="02/17/2022",
            traits={"BWT": 0.378, "WWT": 3.141},
        )

        assert animal.lpn_id == "6401492022FLE059"
        assert animal.sex == "F"
        assert animal.date_of_birth == "02/17/2022"
        assert animal.traits["BWT"] == 0.378

    def test_to_dict(self):
        """Test ProgenyAnimal.to_dict()"""
        animal = ProgenyAnimal(
            lpn_id="TEST123",
            sex="M",
            date_of_birth="01/01/2023",
            traits={"BWT": 0.5},
        )

        result = animal.to_dict()

        assert result["lpn_id"] == "TEST123"
        assert result["sex"] == "M"
        assert result["date_of_birth"] == "01/01/2023"
        assert result["traits"]["BWT"] == 0.5

    def test_minimal_creation(self):
        """Test creating ProgenyAnimal with only lpn_id"""
        animal = ProgenyAnimal(lpn_id="MINIMAL")

        assert animal.lpn_id == "MINIMAL"
        assert animal.sex is None
        assert animal.traits == {}


class TestProgenyExtended:
    """Extended tests for Progeny model"""

    def test_from_api_response_lowercase(self):
        """Test Progeny from camelCase API response"""
        data = {
            "recordCount": 5,
            "records": [
                {
                    "lpnId": "6401492022FLE059",
                    "sex": "F",
                    "dob": "02/17/2022",
                },
                {
                    "lpnId": "6401492022FLE060",
                    "sex": "M",
                    "dob": "02/18/2022",
                },
            ],
        }
        progeny = Progeny.from_api_response(data)

        assert progeny.total_count == 5
        assert len(progeny.animals) == 2
        assert progeny.animals[0].lpn_id == "6401492022FLE059"
        assert progeny.animals[0].sex == "F"
        assert progeny.animals[0].date_of_birth == "02/17/2022"

    def test_page_size_defaults_to_animal_count(self):
        """Test page_size defaults to number of animals when not specified"""
        data = {
            "recordCount": 2,
            "records": [
                {"lpnId": "A1"},
                {"lpnId": "A2"},
            ],
        }
        progeny = Progeny.from_api_response(data)

        assert progeny.page_size == 2


class TestLineage:
    """Test Lineage model"""

    def test_basic_creation(self):
        """Test creating Lineage with subject"""
        subject = LineageAnimal(lpn_id="SUBJECT123", sex="M", status="CURRENT")
        lineage = Lineage(subject=subject)

        assert lineage.subject.lpn_id == "SUBJECT123"
        assert lineage.sire is None
        assert lineage.dam is None
        assert lineage.generations == []

    def test_with_parents(self):
        """Test Lineage with sire and dam"""
        subject = LineageAnimal(lpn_id="CHILD")
        sire = LineageAnimal(lpn_id="SIRE", sex="M")
        dam = LineageAnimal(lpn_id="DAM", sex="F")

        lineage = Lineage(subject=subject, sire=sire, dam=dam)

        assert lineage.subject.lpn_id == "CHILD"
        assert lineage.sire.lpn_id == "SIRE"
        assert lineage.dam.lpn_id == "DAM"

    def test_to_dict(self):
        """Test Lineage.to_dict()"""
        subject = LineageAnimal(lpn_id="SUBJECT123", sex="M")
        lineage = Lineage(
            subject=subject,
            raw_data={"test": "value"},
        )

        result = lineage.to_dict()

        assert result["subject"]["lpn_id"] == "SUBJECT123"
        assert result["subject"]["sex"] == "M"
        assert result["raw_data"]["test"] == "value"

    def test_to_dict_with_generations(self):
        """Test Lineage.to_dict() with generations"""
        subject = LineageAnimal(lpn_id="SUBJECT")
        gen1 = [LineageAnimal(lpn_id="SIRE"), LineageAnimal(lpn_id="DAM")]
        gen2 = [
            LineageAnimal(lpn_id="SS"),
            LineageAnimal(lpn_id="SD"),
            LineageAnimal(lpn_id="DS"),
            LineageAnimal(lpn_id="DD"),
        ]

        lineage = Lineage(
            subject=subject,
            generations=[gen1, gen2],
        )

        result = lineage.to_dict()

        assert len(result["generations"]) == 2
        assert len(result["generations"][0]) == 2
        assert len(result["generations"][1]) == 4
        assert result["generations"][0][0]["lpn_id"] == "SIRE"

    def test_from_api_response_nested_html_format(self):
        """Test Lineage.from_api_response() with real NSIP API format"""
        # Real NSIP API response format with nested HTML
        data = {
            "success": True,
            "data": {
                "lpnId": "6402382024NCS310",
                "content": "<div>NC State Katahdins</div><div>US Hair Index: 102.03</div>"
                "<div>SRC$ Index: 116.56</div><div>DOB: 2/13/2024</div>"
                "<div>Sex: Male</div><div>Status: CURRENT</div>",
                "children": [
                    {
                        "lpnId": "6400462020VPI007",
                        "content": "<div>Virginia Tech</div><div>US Hair Index: 102.61</div>",
                        "children": [
                            {
                                "lpnId": "6400522018NWT012",
                                "content": "<div>Hound River</div><div>US Hair Index: 106.53</div>",
                                "children": [],
                            },
                            {
                                "lpnId": "6400522017NWT082",
                                "content": "<div>Hound River</div><div>US Hair Index: 101.07</div>",
                                "children": [],
                            },
                        ],
                    },
                    {
                        "lpnId": "6402382022NCS087",
                        "content": "<div>NC State</div><div>US Hair Index: 101.89</div>",
                        "children": [],
                    },
                ],
            },
        }

        lineage = Lineage.from_api_response(data)

        # Subject should be parsed
        assert lineage.subject is not None
        assert lineage.subject.lpn_id == "6402382024NCS310"
        assert lineage.subject.farm_name == "NC State Katahdins"
        assert lineage.subject.us_index == 102.03
        assert lineage.subject.date_of_birth == "2/13/2024"
        assert lineage.subject.sex == "Male"
        assert lineage.subject.status == "CURRENT"

        # Parents should be parsed
        assert lineage.sire is not None
        assert lineage.sire.lpn_id == "6400462020VPI007"
        assert lineage.sire.farm_name == "Virginia Tech"
        assert lineage.sire.us_index == 102.61

        assert lineage.dam is not None
        assert lineage.dam.lpn_id == "6402382022NCS087"
        assert lineage.dam.farm_name == "NC State"

        # Generations should be collected
        assert len(lineage.generations) >= 1
        # Generation 0 = parents (2 animals)
        assert len(lineage.generations[0]) == 2
        # Generation 1 = grandparents on sire side (2 animals)
        assert len(lineage.generations[1]) == 2

        # Raw data preserved
        assert lineage.raw_data == data

    def test_from_api_response_unwrapped(self):
        """Test Lineage.from_api_response() without wrapper"""
        data = {
            "lpnId": "TEST123",
            "content": "<div>Test Farm</div><div>US Hair Index: 100.0</div>",
            "children": [],
        }

        lineage = Lineage.from_api_response(data)

        assert lineage.subject is not None
        assert lineage.subject.lpn_id == "TEST123"
        assert lineage.subject.farm_name == "Test Farm"
        assert lineage.sire is None
        assert lineage.dam is None

    def test_from_api_response_empty_children(self):
        """Test Lineage.from_api_response() with no children"""
        data = {
            "success": True,
            "data": {
                "lpnId": "TEST123",
                "content": "<div>Farm</div>",
                "children": [],
            },
        }

        lineage = Lineage.from_api_response(data)

        assert lineage.subject.lpn_id == "TEST123"
        assert lineage.sire is None
        assert lineage.dam is None
        assert lineage.generations == []


class TestParseLineageContent:
    """Tests for _parse_lineage_content helper function"""

    def test_parse_all_fields(self):
        """Test parsing HTML content with all fields"""
        content = (
            "<div>Test Farm Name</div>"
            "<div>US Hair Index: 105.25</div>"
            "<div>SRC$ Index: 112.50</div>"
            "<div>DOB: 1/15/2023</div>"
            "<div>Sex: Female</div>"
            "<div>Status: CURRENT</div>"
        )

        result = _parse_lineage_content(content)

        assert result["farm_name"] == "Test Farm Name"
        assert result["us_index"] == 105.25
        assert result["src_index"] == 112.5
        assert result["date_of_birth"] == "1/15/2023"
        assert result["sex"] == "Female"
        assert result["status"] == "CURRENT"

    def test_parse_us_index_without_hair(self):
        """Test parsing US Index (without 'Hair')"""
        content = "<div>Farm</div><div>US Index: 99.5</div>"

        result = _parse_lineage_content(content)

        assert result["us_index"] == 99.5

    def test_parse_partial_content(self):
        """Test parsing content with only some fields"""
        content = "<div>Just Farm Name</div><div>US Hair Index: 101.0</div>"

        result = _parse_lineage_content(content)

        assert result["farm_name"] == "Just Farm Name"
        assert result["us_index"] == 101.0
        assert "src_index" not in result
        assert "date_of_birth" not in result

    def test_parse_empty_content(self):
        """Test parsing empty content string"""
        result = _parse_lineage_content("")

        assert result == {}


class TestBreedGroup:
    """Test BreedGroup model"""

    def test_basic_creation(self):
        """Test creating BreedGroup"""
        group = BreedGroup(
            id=64,
            name="Hair",
            breeds=[
                {"breedId": 640, "breedName": "Katahdin"},
                {"breedId": 645, "breedName": "St. Croix"},
            ],
        )

        assert group.id == 64
        assert group.name == "Hair"
        assert len(group.breeds) == 2
        assert group.breeds[0]["breedName"] == "Katahdin"

    def test_empty_breeds(self):
        """Test BreedGroup with no breeds"""
        group = BreedGroup(id=99, name="Unknown")

        assert group.id == 99
        assert group.name == "Unknown"
        assert group.breeds == []


class TestSearchCriteriaExtended:
    """Extended tests for SearchCriteria"""

    def test_trait_ranges_in_to_dict(self):
        """Test trait_ranges are included in to_dict"""
        criteria = SearchCriteria(
            trait_ranges={
                "BWT": {"min": -0.5, "max": 0.5},
                "WWT": {"min": 0, "max": 10},
            }
        )

        data = criteria.to_dict()

        assert "traitRanges" in data
        assert data["traitRanges"]["BWT"]["min"] == -0.5
        assert data["traitRanges"]["BWT"]["max"] == 0.5

    def test_flock_id_in_to_dict(self):
        """Test flock_id is included in to_dict"""
        criteria = SearchCriteria(flock_id="FLOCK123")

        data = criteria.to_dict()

        assert data["flockId"] == "FLOCK123"

    def test_date_filters(self):
        """Test born_after and born_before in to_dict"""
        criteria = SearchCriteria(
            born_after="2020-01-01",
            born_before="2022-12-31",
        )

        data = criteria.to_dict()

        assert data["bornAfter"] == "2020-01-01"
        assert data["bornBefore"] == "2022-12-31"

    def test_status_filter(self):
        """Test status filter in to_dict"""
        criteria = SearchCriteria(status="SOLD")

        data = criteria.to_dict()

        assert data["status"] == "SOLD"


class TestAnimalDetailsEdgeCases:
    """Edge case tests for AnimalDetails"""

    def test_flock_count_as_non_digit_string(self):
        """Test flock_count with non-digit string returns None"""
        data = {
            "success": True,
            "data": {
                "flockCount": "multiple",
                "searchResultViewModel": {"lpnId": "TEST123"},
            },
        }
        animal = AnimalDetails.from_api_response(data)

        assert animal.flock_count is None

    def test_empty_registration_number(self):
        """Test empty registration number is preserved"""
        data = {
            "success": True,
            "data": {
                "searchResultViewModel": {
                    "lpnId": "TEST123",
                    "regNumber": "",
                },
            },
        }
        animal = AnimalDetails.from_api_response(data)

        assert animal.registration_number == ""

    def test_all_traits_parsed(self):
        """Test all supported traits are parsed from nested format"""
        data = {
            "success": True,
            "data": {
                "searchResultViewModel": {
                    "lpnId": "TEST123",
                    "bwt": 0.5,
                    "accbwt": 0.80,
                    "wwt": 2.5,
                    "accwwt": 0.75,
                    "pwwt": 3.0,
                    "accpwwt": 0.70,
                    "ywt": 4.0,
                    "accywt": 0.65,
                    "fat": 0.1,
                    "accfat": 0.60,
                    "emd": 0.2,
                    "accemd": 0.55,
                    "nlb": 0.05,
                    "accnlb": 0.50,
                    "nwt": 1.0,
                    "accnwt": 0.45,
                    "pwt": 2.0,
                    "accpwt": 0.40,
                    "dag": 0.3,
                    "accdag": 0.35,
                    "wgr": 0.4,
                    "accwgr": 0.30,
                    "wec": 0.5,
                    "accwec": 0.25,
                    "fec": 0.6,
                    "accfec": 0.20,
                },
            },
        }
        animal = AnimalDetails.from_api_response(data)

        # All 13 traits should be parsed
        expected_traits = [
            "BWT",
            "WWT",
            "PWWT",
            "YWT",
            "FAT",
            "EMD",
            "NLB",
            "NWT",
            "PWT",
            "DAG",
            "WGR",
            "WEC",
            "FEC",
        ]
        for trait in expected_traits:
            assert trait in animal.traits, f"Missing trait: {trait}"

    def test_accuracy_none_handled(self):
        """Test None accuracy is handled correctly"""
        data = {
            "success": True,
            "data": {
                "searchResultViewModel": {
                    "lpnId": "TEST123",
                    "bwt": 0.5,
                    "accbwt": None,
                },
            },
        }
        animal = AnimalDetails.from_api_response(data)

        assert animal.traits["BWT"].accuracy is None

    def test_accuracy_zero_handled(self):
        """Test zero accuracy is handled correctly"""
        data = {
            "success": True,
            "data": {
                "searchResultViewModel": {
                    "lpnId": "TEST123",
                    "bwt": 0.5,
                    "accbwt": 0,
                },
            },
        }
        animal = AnimalDetails.from_api_response(data)

        # 0 accuracy should result in None (since 0 is falsy in the condition)
        assert animal.traits["BWT"].accuracy is None
