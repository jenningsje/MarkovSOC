# -------------------------------
# MarkovSOC Helper Makefile
# -------------------------------

# Build images
build:
	docker-compose build sf-enricher

# Start all services in detached mode
up:
	docker-compose up -d

# Stop all services
down:
	docker-compose down

# Import OpenSearch Dashboards
dashboards:
	@echo "Import markov_dashboard.json manually via http://localhost:5601"

# Full deploy: build, up, db-setup
deploy: build up db-setup dashboards
	@echo "✅ MarkovSOC stack is live!"
	@echo " - OpenSearch Dashboards: http://localhost:5601"