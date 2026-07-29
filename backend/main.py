"""
main.py - FastAPI Backend untuk TONDI Dashboard."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from services.dashboard import get_dashboard_stats
from services.locations import get_all_locations, get_location_detail
from services.priorities import get_priorities
from services.anomalies import get_anomalies
from services.reviews import get_reviews, get_filter_options
from services.trends import get_review_trends
from services.recommendations import get_location_recommendations

app = FastAPI(title="TONDI API", version="1.0.0")

@app.on_event("startup")
def warmup_cache():
    """Warm up all data caches on startup so first request is fast."""
    import time
    t0 = time.time()
    from utils.data_loader import load_reviews, load_metadata
    load_reviews()
    load_metadata()
    elapsed = time.time() - t0
    print(f"[TONDI] Cache warmed: {elapsed:.2f}s ({len(load_reviews())} reviews, {len(load_metadata())} metadata)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"name": "TONDI API", "version": "1.0.0", "endpoints": ["/api/dashboard","/api/locations","/api/locations/{name}","/api/priorities","/api/anomalies","/api/reviews","/api/filters","/api/trends","/api/recommendations/{location}"]}

@app.get("/api/dashboard")
def dashboard():
    return get_dashboard_stats()

@app.get("/api/locations")
def locations(
    region: str = Query(None, description="Filter wilayah"),
    topic: str = Query(None, description="Filter topik isu"),
):
    return get_all_locations(region, topic)

@app.get("/api/locations/{location_name}")
def location_detail(location_name: str):
    r = get_location_detail(location_name)
    if r is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Lokasi '{location_name}' tidak ditemukan")
    return r

@app.get("/api/priorities")
def priorities(limit: int = Query(20)):
    return {"priorities": get_priorities(limit)}

@app.get("/api/anomalies")
def anomalies(threshold: float = Query(2.0)):
    return {"anomalies": get_anomalies(threshold)}

@app.get("/api/reviews")
def reviews(location: str = None, sentiment: str = None, topic: str = None, limit: int = 50):
    return {"reviews": get_reviews(location, sentiment, topic, limit)}

@app.get("/api/filters")
def filters():
    from utils.data_loader import get_regions
    opts = get_filter_options()
    opts["regions"] = get_regions()
    return opts

@app.get("/api/trends")
def trends(days: int = Query(7)):
    return {"trends": get_review_trends(days)}

@app.get("/api/recommendations/{location_name}")
def recommendations(location_name: str):
    return {"recommendations": get_location_recommendations(location_name), "location": location_name}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
