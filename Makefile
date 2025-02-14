USE_RYE := true

ifeq ($(USE_RYE),true)
EXECUTABLE := rye run
else
EXECUTABLE :=
endif

# Run
.PHONY: run
run:
	$(EXECUTABLE) python src/backend/run.py

.PHONY: interact
interact:
	$(EXECUTABLE) python cli/interact.py

.PHONY: add-facts
add-facts:
	$(EXECUTABLE) python cli/add_facts.py

# Docker
.PHONY: docker-build
docker-build:
	docker build -t backend .

.PHONY: docker-run
docker-run:
	docker run -p 8000:8000 backend

.PHONY: dc.up
dc.up:
	docker compose up -d --remove-orphans

.PHONY: dc.down
dc.down:
	docker compose down

.PHONY: dc.down-delete
dc.down-delete:
	docker compose down -v

.PHONY: dc.ps
dc.ps:
	docker compose ps

.PHONY: dc.logs
dc.logs:
	docker compose logs -f

.PHONY: dc.restart
dc.restart:
	docker compose restart

.PHONY: dc.rebuild
dc.rebuild:
	docker compose up -d --build

# Formatters
.PHONY: ruff
ruff:
	$(EXECUTABLE) ruff format src cli
	$(EXECUTABLE) ruff check src cli --fix --preview

.PHONY: format
format: ruff

# Linting
.PHONY: check-ruff
check-ruff:
	$(EXECUTABLE) ruff check src cli --preview

.PHONY: check-format
check-format: check-ruff

.PHONY: flake8
flake8:
	$(EXECUTABLE) flake8 src cli

.PHONY: mypy
mypy:
	$(EXECUTABLE) mypy --config-file pyproject.toml src cli

.PHONY: lint
lint: check-ruff mypy flake8

# Check
.PHONY: check
check: format lint
