#!/usr/bin/env python3
import os
import requests
import json
from datetime import datetime
import geoip2.database
from elasticsearch import Elasticsearch

# Config from environment
SF_API_URL = os.environ.get("SF_API_URL", "http://spiderfoot:5001/api/v3")
SF_API_KEY = os.environ.get("SF_API_KEY", "changeme123")
OS_HOST = os.environ.get("OS_HOST", "opensearch")
OS_PORT = os.environ.get("OS_PORT", "9200")
OS_INDEX = os.environ.get("OS_INDEX", "alerts")
GEOIP_DB = "/usr/share/GeoIP/GeoLite2-City.mmdb"  # optional

# Elasticsearch client
es = Elasticsearch([{"host": OS_HOST, "port": OS_PORT}])

def geo_lookup(ip):
    try:
        import geoip2.database
        reader = geoip2.database.Reader(GEOIP_DB)
        resp = reader.city(ip)
        reader.close()
        return {
            "country": resp.country.iso_code,
            "location": {"lat": resp.location.latitude, "lon": resp.location.longitude}
        }
    except:
        return {}

def enrich_ip(ip):
    # SpiderFoot API call
    headers = {"Authorization": f"Bearer {SF_API_KEY}"}
    r = requests.get(f"{SF_API_URL}/scan?target={ip}", headers=headers)
    scan_data = r.json()
    
    # Prepare document for OpenSearch
    doc = {
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat(),
        "reputation_score": scan_data.get("risk_score", 0),
        "tags": scan_data.get("tags", []),
        "enriched": True,
        "geo": geo_lookup(ip)
    }
    
    # Push to OpenSearch
    es.index(index=OS_INDEX, document=doc)
    print(f"[+] Enriched {ip} -> OpenSearch")

if __name__ == "__main__":
    # Example: read IPs from sf_cache/ip_list.json
    ip_list_file = "/app/sf_cache/ip_list.json"
    if os.path.exists(ip_list_file):
        with open(ip_list_file) as f:
            ips = json.load(f)
    else:
        ips = ["8.8.8.8", "1.1.1.1"]  # fallback test IPs

    for ip in ips:
        enrich_ip(ip)
