# Remediation Tasks

**Generated**: 2025-12-24
**Project**: NSIP API Client
**Total Findings**: 107 (2 Critical, 14 High, 48 Medium, 43 Low)

---

## Critical (Do Immediately)

- [ ] `src/nsip_skills/mating_optimizer.py:188-199` - Fix N+1 query pattern by pre-fetching lineage data - PERFORMANCE
- [ ] `src/nsip_skills/progeny_analysis.py:102-137` - Fix N+1 query pattern by batch fetching progeny details - PERFORMANCE

---

## High Priority (This Sprint)

### Performance (5)
- [ ] `src/nsip_client/client.py:363-388` - Parallelize 3 API calls in search_by_lpn using ThreadPoolExecutor - PERFORMANCE
- [ ] `src/nsip_mcp/mcp_tools.py:257-291` - Add async wrappers for blocking HTTP calls in MCP tools - PERFORMANCE
- [ ] `src/nsip_mcp/metrics.py:40-52` - Bound metrics lists using deque(maxlen=10000) to prevent memory leak - PERFORMANCE
- [ ] `src/nsip_skills/inbreeding.py:317-347` - Add memoization to reduce O(n²) path calculation - PERFORMANCE
- [ ] `src/nsip_mcp/context.py:66-149` - Serialize JSON once and reuse to reduce CPU overhead - PERFORMANCE

### Architecture (3)
- [ ] `src/nsip_mcp/mcp_tools.py` - Decompose 829-line file into api_tools.py, shepherd_tools.py, validation.py - ARCHITECTURE
- [ ] `src/nsip_mcp/cache.py + nsip_skills/common/nsip_wrapper.py` - Unify caching implementations - ARCHITECTURE
- [ ] `src/nsip_mcp/shepherd/domains/*.py` - Create DomainHandler interface - ARCHITECTURE

### Code Quality (1)
- [ ] `src/nsip_skills/mating_optimizer.py:130-132` - Add warning logging when inbreeding calculation fails - CODE_QUALITY

### Documentation (3)
- [ ] `docs/CHANGELOG.md` - Add entries for versions 1.3.0-1.3.7 - DOCUMENTATION
- [ ] `README.md, docs/mcp-server.md` - Update version references to current (1.3.5/1.3.7) - DOCUMENTATION
- [ ] `docs/API_REFERENCE.md` - Add MCP Tools section - DOCUMENTATION

### Test Coverage (2)
- [ ] `src/nsip_mcp/metrics.py:129-280` - Add tests for extended metrics (SC-008/009/010) - TEST_COVERAGE
- [ ] `tests/unit/test_metrics.py` - Add thread safety tests for ServerMetrics - TEST_COVERAGE

---

## Medium Priority (Next 2-3 Sprints)

### Security (1)
- [ ] `src/nsip_client/client.py:36` - Investigate HTTPS support for NSIP API - SECURITY

### Performance (9)
- [ ] `src/nsip_mcp/cache.py:135-136` - Use orjson or cache serialized keys - PERFORMANCE
- [ ] `src/nsip_skills/inbreeding.py:209-225` - Use Counter for O(n) common ancestor search - PERFORMANCE
- [ ] `src/nsip_skills/common/nsip_wrapper.py:96-113` - Keep hot cache entries in memory - PERFORMANCE
- [ ] `src/nsip_skills/common/nsip_wrapper.py:224-249` - Add MAX_PAGES safety limit - PERFORMANCE
- [ ] `src/nsip_mcp/resources/flock_resources.py:97-108` - Pass filter to API if supported - PERFORMANCE
- [ ] `src/nsip_skills/selection_index.py:223` - Move statistics import to module level - PERFORMANCE
- [ ] `src/nsip_client/client.py:48-51` - Configure HTTPAdapter with connection pooling - PERFORMANCE
- [ ] `src/nsip_mcp/knowledge_base/loader.py:37-62` - Pre-load YAML files at startup - PERFORMANCE
- [ ] `src/nsip_client/models.py:94,326,444` - Move asdict import to module level - PERFORMANCE

### Architecture (8)
- [ ] `src/nsip_skills/*.py` - Create client provider to eliminate instantiation boilerplate - ARCHITECTURE
- [ ] `src/nsip_mcp/shepherd/regions.py:11-61` - Move NSIP_REGIONS to YAML only - ARCHITECTURE
- [ ] `src/nsip_mcp/shepherd/agent.py:248-549` - Delegate _handle_* methods to domain handlers - ARCHITECTURE
- [ ] `src/nsip_skills/common/data_models.py` - Document relationship with client models - ARCHITECTURE
- [ ] `src/nsip_mcp/metrics.py` - Separate MetricsCollector from HealthAssessor - ARCHITECTURE
- [ ] `src/nsip_mcp/shepherd/agent.py:90-183` - Move keywords to domain handlers - ARCHITECTURE
- [ ] `src/nsip_mcp/metrics.py` (end) - Defer singleton instantiation - ARCHITECTURE
- [ ] `src/nsip_mcp/mcp_tools.py:635,679,724,767,810` - Use dependency injection for prompts - ARCHITECTURE

### Code Quality (9)
- [ ] `src/nsip_skills/*.py` - Create context manager for client lifecycle (~150 lines saved) - CODE_QUALITY
- [ ] `src/nsip_mcp/prompts/skill_prompts.py:83-84,155-156,273-274` - Replace `except Exception: pass` with logging - CODE_QUALITY
- [ ] `src/nsip_skills/inbreeding.py:204-206` - Add logging for ancestor fetch exceptions - CODE_QUALITY
- [ ] `src/nsip_skills/mating_optimizer.py:146-155` - Create MatingPlanConfig dataclass (8 params) - CODE_QUALITY
- [ ] `src/nsip_skills/common/nsip_wrapper.py:251-260` - Create SearchConfig dataclass (7 params) - CODE_QUALITY
- [ ] `src/nsip_mcp/prompts/shepherd_prompts.py:147-237` - Extract context-building helpers - CODE_QUALITY
- [ ] `src/nsip_skills/progeny_analysis.py:102-140` - Extract inner loop logic (4 levels) - CODE_QUALITY
- [ ] `src/nsip_skills/trait_planner.py:17-30` - Import heritabilities from knowledge base - CODE_QUALITY
- [ ] `src/nsip_skills/*.py` - Add module-level docstrings - CODE_QUALITY

### Test Coverage (7)
- [ ] `src/nsip_mcp/cli.py:32-37` - Add CLI exception path tests - TEST_COVERAGE
- [ ] `src/nsip_mcp/mcp_tools.py:621-829` - Add Shepherd empty messages edge case tests - TEST_COVERAGE
- [ ] `src/nsip_mcp/context.py:354-360` - Add accuracy normalization tests - TEST_COVERAGE
- [ ] `src/nsip_mcp/cache.py:117-136` - Add non-serializable type exception test - TEST_COVERAGE
- [ ] `src/nsip_mcp/context.py:330` - Add non-dict progeny handling tests - TEST_COVERAGE
- [ ] `src/nsip_skills/*.py` - Run coverage report for edge cases - TEST_COVERAGE
- [ ] `src/nsip_mcp/tools.py` - Add reset_client singleton tests - TEST_COVERAGE

### Documentation (14)
- [ ] `src/nsip_mcp/transport.py` - Add module docstring - DOCUMENTATION
- [ ] `src/nsip_mcp/shepherd/domains/*.py` - Add class docstrings to all domain handlers - DOCUMENTATION
- [ ] `src/nsip_mcp/shepherd/persona.py` - Add ShepherdPersona class docstring - DOCUMENTATION
- [ ] `src/nsip_skills/ebv_analysis.py` - Add module docstring - DOCUMENTATION
- [ ] `src/nsip_skills/mating_optimizer.py` - Add module docstring - DOCUMENTATION
- [ ] `src/nsip_skills/progeny_analysis.py` - Add module docstring - DOCUMENTATION
- [ ] `src/nsip_skills/recommendation_engine.py` - Add module docstring - DOCUMENTATION
- [ ] `src/nsip_skills/trait_planner.py` - Add module docstring - DOCUMENTATION
- [ ] `src/nsip_skills/flock_stats.py` - Add module docstring - DOCUMENTATION
- [ ] `src/nsip_skills/selection_index.py` - Add module docstring - DOCUMENTATION
- [ ] `src/nsip_skills/ancestry_builder.py` - Add module docstring - DOCUMENTATION
- [ ] `README.md` - Document MCP_HOST and MCP_PATH env vars - DOCUMENTATION
- [ ] `examples/` - Add skills_usage.py example - DOCUMENTATION
- [ ] `docs/API_REFERENCE.md` - Add Lineage/LineageAnimal models - DOCUMENTATION

---

## Low Priority (Backlog)

### Security (6)
- [ ] `src/nsip_mcp/transport.py:33-35` - Document 0.0.0.0 binding security considerations
- [ ] `src/nsip_skills/common/spreadsheet_io.py:162` - Explicitly validate Google credentials path
- [ ] `src/nsip_skills/common/nsip_wrapper.py:68-69` - Validate cache_dir paths
- [ ] `src/nsip_mcp/mcp_tools.py:103-104` - Consider sanitizing error messages in production
- [ ] `src/nsip_mcp/mcp_tools.py` - Consider adding rate limiting
- [ ] `scripts/build_packages.py:41-46` - False positive (secure implementation)

### Performance (6)
- [ ] `src/nsip_client/models.py:376-416` - Precompile regex patterns at module level
- [ ] `src/nsip_skills/common/data_models.py:197-213` - Convert all_ancestors() to generator
- [ ] `src/nsip_mcp/mcp_tools.py:95-117` - Fix double validation recording
- [ ] `src/nsip_skills/inbreeding.py:191-192` - Optimize path string building
- [ ] `src/nsip_skills/recommendation_engine.py:214` - Remove unused constraints parameter
- [ ] Various main() functions - Move json/argparse imports to module level

### Architecture (6)
- [ ] `src/nsip_mcp/knowledge_base/loader.py:31-34` - Move KnowledgeBaseError to errors.py
- [ ] `src/nsip_mcp/context.py:22-23` - Centralize threshold constants
- [ ] `src/nsip_mcp/shepherd/domains/breeding.py:19` - Extract common formatting logic
- [ ] `src/nsip_client/cli.py, nsip_mcp/cli.py` - Consider click/typer for CLI consistency
- [ ] Various internal functions - Add type hints
- [ ] `src/nsip_skills/inbreeding.py:22` - Remove backwards-compat alias

### Code Quality (12)
- [ ] `src/nsip_skills/inbreeding.py:22` - Remove unused format_inbreeding_report alias
- [ ] `src/nsip_skills/common/formatters.py:262-266` - Add emojis or remove empty dict
- [ ] Various files - Standardize dict comprehension vs loop style
- [ ] `shepherd_prompts.py, skill_prompts.py` - Standardize string building patterns
- [ ] `src/nsip_skills/common/nsip_wrapper.py:124-125` - Log cache write failures at DEBUG
- [ ] `examples/basic_usage.py:38` - Use realistic sample LPN or document as placeholder
- [ ] Various minor style inconsistencies

### Test Coverage (5)
- [ ] `tests/test_cli.py` - Add JSON output format verification
- [ ] `src/nsip_skills/inbreeding.py` - Add exception handling tests for _expand_parent_node
- [ ] `src/nsip_mcp/resources/animal_resources.py` - Add resource cache integration tests
- [ ] `src/nsip_mcp/mcp_tools.py:139` - Add validate_breed_id type tests
- [ ] `src/nsip_skills/ebv_analysis.py:138` - Add single-value std deviation test

### Documentation (8)
- [ ] `src/nsip_client/models.py` - Enhance _parse_lineage_content docstring
- [ ] `src/nsip_mcp/resources/*.py` - Enhance resource docstrings with URI examples
- [ ] `src/nsip_mcp/mcp_tools.py`, `llms.txt` - Update "14 tools" to "15 tools"
- [ ] `src/nsip_client/exceptions.py` - Add `-> None` return type hints
- [ ] `docs/` - Create TROUBLESHOOTING.md
- [ ] `docs/` - Create ARCHITECTURE.md
- [ ] `README.md` - Add explicit MIT license mention
- [ ] Various - Minor docstring enhancements

---

## Category Summary

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Security | 0 | 0 | 1 | 6 | 7 |
| Performance | 2 | 5 | 9 | 6 | 22 |
| Architecture | 0 | 3 | 8 | 6 | 17 |
| Code Quality | 0 | 1 | 9 | 12 | 22 |
| Test Coverage | 0 | 2 | 7 | 5 | 14 |
| Documentation | 0 | 3 | 14 | 8 | 25 |
| **TOTAL** | **2** | **14** | **48** | **43** | **107** |

---

*Import to issue tracker or convert to GitHub Issues*
