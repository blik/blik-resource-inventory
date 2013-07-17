
TEST_RUNNER:=./tests/runTests

export PYTHONPATH=./

compile:
	@echo 'This method is not implemented'; ./rpmbuild.sh 0.1

clean:
	@echo "rm -rf ./dist"; rm -rf ./dist

test:
	@$(TEST_RUNNER)
