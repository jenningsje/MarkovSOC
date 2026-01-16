import requests
import json
from opensearchpy import OpenSearch

# SpiderFoot API
SF_API_URL = "http://spiderfoot:5001/api/v3"
SF_API_KEY = "changeme123"

# OpenSearch config
OS_HOST = "opensearch"
OS_PORT = 9200
OS_INDEX = "alerts"

os_client = OpenSearch(
    hosts=[{"host": OS_HOST, "port": OS_PORT}],
    http_compress=True
)

def get_suspicious_ips():
    # Query OpenSearch for new suspicious IPs
    query = {
        "query": {
            "match": {"enriched": False}  # only not enriched yet
        }
    }
    resp = os_client.search(index=OS_INDEX, body=query)
    return [hit["_source"]["ip"] for hit in resp["hits"]["hits"]]

def enrich_ip(ip):
    payload = {
        "module": "sfp_ip",    # scan an IP
        "target": ip,
        "options": {"deep": True}
    }
    headers = {"APIKEY": SF_API_KEY}
    r = requests.post(f"{SF_API_URL}/scan/new", headers=headers, json=payload)
    if r.status_code == 200:
        scan_id = r.json().get("scanid")
        return scan_id
    return None

def mark_enriched(ip):
    os_client.update_by_query(
        index=OS_INDEX,
        body={
            "script": {"source": "ctx._source.enriched=true"},
            "query": {"match": {"ip": ip}}
        }
    )

if __name__ == "__main__":
    ips = get_suspicious_ips()
    for ip in ips:
        scan_id = enrich_ip(ip)
        if scan_id:
            print(f"Started SpiderFoot scan for {ip}: {scan_id}")
            mark_enriched(ip)

