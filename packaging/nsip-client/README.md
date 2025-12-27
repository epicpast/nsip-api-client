# nsip-client

Python client for the NSIP (National Sheep Improvement Program) Search API.

## Installation

```bash
pip install nsip-client
```

## Quick Start

```python
from nsip_client import NSIPClient

client = NSIPClient()

# Search for animals
animals = client.search_animals(breed_id=486, limit=10)

# Get animal details
details = client.get_animal_details("6332-12345")

# Get lineage
lineage = client.get_lineage("6332-12345")
```

## Documentation

Full documentation is available at the [project repository](https://github.com/epicpast/nsip-api-client).

## License

MIT License - see [LICENSE](https://github.com/epicpast/nsip-api-client/blob/main/LICENSE) for details.
