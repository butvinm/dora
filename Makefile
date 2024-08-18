.PHONY: run_tests
run_tests:
	python tests/test.py

.PHONY: record_tests
record_tests:
	DORA_SNAPSHOT_RECORD=true python tests/test.py
