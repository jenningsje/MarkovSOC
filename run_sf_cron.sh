#!/bin/bash
# run_sf_cron.sh - runs sf_enrich.py every 5 minutes

# make sure environment variables are loaded
export SF_API_URL=${SF_API_URL:-http://spiderfoot:5001/api/v3}
export SF_API_KEY=${SF_API_KEY:-changeme123}
export OS_HOST=${OS_HOST:-opensearch}
export OS_PORT=${OS_PORT:-9200}
export OS_INDEX=${OS_INDEX:-alerts}

echo "Starting SpiderFoot enrichment cron..."
# Run the script every 5 minutes
while true; do
    echo "[*] Running SpiderFoot Enricher..."
    python /app/sf_enricher.py
    echo "[*] Sleeping 5 minutes..."
    sleep 300
done
