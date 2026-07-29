import React, { useState, useEffect, useRef } from "react";
import {
  BarChart3,
  MapPin,
  AlertTriangle,
  Star,
  TrendingUp,
  Clock,
  ChevronDown,
  MessageSquare,
  CheckCircle2,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix Leaflet default icon path for webpack/vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const API_BASE = "https://astronomy-thesaurus-lavender.ngrok-free.dev/api";

// Review Card component — extracted for reusability
function ReviewCard({ review }) {
  return (
    <div className="bg-gradient-to-br from-slate-50 to-white p-3.5 rounded-xl border border-slate-200/70 shadow-sm hover:shadow-md hover:border-slate-300/70 transition-all duration-200">
      <div className="flex justify-between items-start mb-2">
        <span className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
          <span className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 flex items-center justify-center text-[9px] font-bold text-blue-600">
            {(review.author || "A")[0]}
          </span>
          {review.author || "Anonim"}
        </span>
        <div className="flex items-center gap-2">
          {review.rating && (
            <div className="flex items-center gap-0.5 bg-amber-50/80 px-1.5 py-0.5 rounded-md">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  size={9}
                  className={
                    i < (review.rating || 3)
                      ? "text-amber-400 fill-amber-400"
                      : "text-amber-200/50"
                  }
                />
              ))}
            </div>
          )}
          {review.date && (
            <span className="text-[10px] text-slate-400 tabular-nums">
              {review.date?.slice(0, 10) || "-"}
            </span>
          )}
        </div>
      </div>
      <p className="text-sm text-slate-600 leading-relaxed italic border-l-2 border-slate-200 pl-3">
        "{review.text?.slice(0, 200)}
        {review.text?.length > 200 ? "..." : ""}"
      </p>
      <div className="flex gap-2 mt-2.5">
        <span
          className={
            "text-[10px] font-semibold px-2.5 py-0.5 rounded-full ring-1 " +
            (review.sentiment === "Positif"
              ? "bg-emerald-50 text-emerald-700 ring-emerald-200/50"
              : review.sentiment === "Negatif"
                ? "bg-rose-50 text-rose-700 ring-rose-200/50"
                : "bg-slate-50 text-slate-600 ring-slate-200/50")
          }
        >
          {review.sentiment}
        </span>
        {review.topic && (
          <span className="text-[10px] font-semibold px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 ring-1 ring-blue-200/50">
            {review.topic}
          </span>
        )}
      </div>
    </div>
  );
}

// Map controller — MUST be outside App() to avoid remount on every render
function MapFlyController({ mapRef }) {
  const map = useMap();
  useEffect(() => {
    mapRef.current = map;
    return () => {
      mapRef.current = null;
    };
  }, [map, mapRef]);
  return null;
}

export default function App() {
  const [selectedIssue, setSelectedIssue] = useState("Semua Isu");
  const [selectedRegion, setSelectedRegion] = useState("Semua Wilayah");

  // API State
  const [dash, setDash] = useState(null);
  const [locations, setLocations] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [trends, setTrends] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [filters, setFilters] = useState(null);
  const [selLoc, setSelLoc] = useState(null);
  const [locDetail, setLocDetail] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);
  const mapRef = useRef(null);
  const [locationImages, setLocationImages] = useState({});

  // Image mapping from Excel database + normalized matching
  const [excelImages, setExcelImages] = useState({});
  const [excelNormalized, setExcelNormalized] = useState({});
  useEffect(() => {
    fetch("/data/location-images.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data) {
          if (data.images) setExcelImages(data.images);
          if (data.normalized) setExcelNormalized(data.normalized);
          fetch(API_BASE + "/dashboard", {
            headers: { "ngrok-skip-browser-warning": "true" },
          });
        }
      })
      .catch(() => {});
  }, []);

  // Normalize name for fuzzy matching
  function normalizeName(n) {
    return n
      .toLowerCase()
      .replace(/[-.']/g, " ")
      .replace(/[^a-z0-9 ]/g, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  // Build coord lookup: location name -> {lat, lng}
  function getCoord(name) {
    const found = locations.find(
      (l) => l.name === name && l.latitude && l.longitude,
    );
    return found ? { lat: found.latitude, lng: found.longitude } : null;
  }

  // Get image URL: Excel DB > Wikipedia > null
  function getImageUrl(name) {
    // 1. Try exact match from Excel DB
    if (excelImages[name]) return excelImages[name];
    // 2. Try normalized match from Excel DB
    const norm = normalizeName(name);
    if (excelNormalized[norm]) return excelNormalized[norm];
    // 3. Try Wikipedia fallback
    if (locationImages[name]) return locationImages[name];
    return null;
  }

  // Fetch FREE Wikipedia thumbnail for a location (CC-licensed images)
  async function getWikiThumb(name) {
    try {
      const url =
        "https://id.wikipedia.org/w/api.php?action=query&prop=pageimages&piprop=thumbnail&pithumbsize=400&titles=" +
        encodeURIComponent(name) +
        "&format=json&origin=*";
      const r = await fetch(url);
      const data = await r.json();
      const pages = data.query.pages;
      const firstKey = Object.keys(pages)[0];
      if (firstKey !== "-1" && pages[firstKey].thumbnail) {
        return pages[firstKey].thumbnail.source;
      }
    } catch (e) {}
    return null;
  }

  // Fetch all data on mount
  useEffect(() => {
    (async () => {
      try {
        const [d, l, p, a, t, r, f] = await Promise.all([
          fetch(API_BASE + "/dashboard").then((r) => r.json()),
          fetch(API_BASE + "/locations").then((r) => r.json()),
          fetch(API_BASE + "/priorities?limit=10").then((r) => r.json()),
          fetch(API_BASE + "/anomalies").then((r) => r.json()),
          fetch(API_BASE + "/trends?days=7").then((r) => r.json()),
          fetch(API_BASE + "/reviews?limit=10").then((r) => r.json()),
          fetch(API_BASE + "/filters").then((r) => r.json()),
        ]);
        setDash(d);
        setLocations(l.locations || []);
        setPriorities(p.priorities || []);
        setAnomalies(a.anomalies || []);
        setTrends(t.trends || []);
        setReviews(r.reviews || []);
        setFilters(f);
        if (p.priorities && p.priorities.length > 0) {
          clickLoc(p.priorities[0].name);
        }
      } catch (e) {
        setErr("Gagal terhubung ke backend. Jalankan server di port 8000.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Get relevant reviews that support recommendation topics
  function getRelevantReviews() {
    // From locDetail.reviews_by_topic, pick reviews matching recommendation topics
    if (!locDetail?.reviews_by_topic || recommendations.length === 0) {
      return [];
    }
    // Get top topic(s) from recommendations
    const recTopics = recommendations.map((r) => r.topic).filter(Boolean);
    if (recTopics.length === 0) return [];

    const result = [];
    for (const topic of recTopics) {
      const topicReviews = locDetail.reviews_by_topic[topic];
      if (topicReviews) {
        for (const r of topicReviews) {
          result.push({ ...r, topic });
        }
      }
    }
    // Also add general negative reviews
    const otherReviews = locDetail.recent_reviews || [];
    for (const r of otherReviews) {
      if (r.sentiment === "Negatif" || r.sentiment === "Netral") {
        result.push(r);
      }
    }
    // Deduplicate by text content
    const seen = new Set();
    return result
      .filter((r) => {
        if (seen.has(r.text)) return false;
        seen.add(r.text);
        return true;
      })
      .slice(0, 5);
  }

  // Fetch Wikipedia thumbnails (separate effect, non-blocking)
  useEffect(() => {
    if (priorities.length === 0) return;
    let cancelled = false;
    (async () => {
      const names = priorities.slice(0, 20).map((i) => i.name);
      const imgs = {};
      // Stagger requests to respect Wikipedia rate limits
      for (let i = 0; i < names.length; i++) {
        if (cancelled) break;
        await new Promise((r) => setTimeout(r, 150));
        const imgUrl = await getWikiThumb(names[i]);
        if (imgUrl && !cancelled) imgs[names[i]] = imgUrl;
      }
      if (!cancelled) setLocationImages(imgs);
    })();
    return () => {
      cancelled = true;
    };
  }, [priorities]);

  async function clickLoc(name) {
    setSelLoc(name);
    // Try to fly map to location (from list coords first, then from detail)
    let flyToCoord = null;
    const listCoord = getCoord(name);
    if (listCoord && listCoord.lat) {
      flyToCoord = listCoord;
    }
    if (flyToCoord && mapRef.current) {
      mapRef.current.flyTo([flyToCoord.lat, flyToCoord.lng], 13, {
        duration: 1.2,
      });
    }
    try {
      const [locRes, recRes] = await Promise.all([
        fetch(API_BASE + "/locations/" + encodeURIComponent(name)).then((r) =>
          r.ok ? r.json() : null,
        ),
        fetch(API_BASE + "/recommendations/" + encodeURIComponent(name)).then(
          (r) => (r.ok ? r.json() : null),
        ),
      ]);
      if (locRes) {
        setLocDetail(locRes);
        // Fallback: use coordinate from detail endpoint
        if (
          !flyToCoord &&
          locRes.coordinate &&
          locRes.coordinate.lat &&
          mapRef.current
        ) {
          mapRef.current.flyTo(
            [locRes.coordinate.lat, locRes.coordinate.lng],
            13,
            { duration: 1.2 },
          );
        }
      }
      if (recRes) setRecommendations(recRes.recommendations || []);
    } catch (e) {}
  }

  // Re-fetch locations with region + topic filters
  async function fetchLocations(region, issue) {
    const params = new URLSearchParams();
    if (region && region !== "Semua Wilayah") params.set("region", region);
    if (issue && issue !== "Semua Isu") params.set("topic", issue);
    const qs = params.toString();
    try {
      const r = await fetch(API_BASE + "/locations" + (qs ? "?" + qs : ""));
      if (r.ok) {
        const data = await r.json();
        setLocations(data.locations || []);
      }
    } catch (e) {}
  }

  // Re-fetch when region changes
  async function handleRegionChange(region) {
    setSelectedRegion(region);
    setSelLoc(null);
    setLocDetail(null);
    setRecommendations([]);
    await fetchLocations(region, selectedIssue);
  }

  // Re-fetch when issue changes
  async function handleIssueChange(issue) {
    setSelectedIssue(issue);
    setSelLoc(null);
    setLocDetail(null);
    setRecommendations([]);
    await fetchLocations(selectedRegion, issue);
  }

  // Skeleton shimmer component
  function Skeleton({ className }) {
    return (
      <div className={`animate-pulse bg-slate-200 rounded ${className}`} />
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-800 font-sans p-4 xl:p-6 animate-fadeIn">
        <style>{`@keyframes fadeIn { from { opacity:0; } to { opacity:1; } } .animate-fadeIn { animation: fadeIn 0.3s ease-out; }`}</style>
        {/* Header skeleton */}
        <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <Skeleton className="h-8 w-28 mb-2" />
            <Skeleton className="h-4 w-72 mb-1" />
            <Skeleton className="h-3 w-56" />
          </div>
          <Skeleton className="h-9 w-52 rounded-lg" />
        </div>
        {/* 3-column skeleton grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Col 1 */}
          <div className="flex flex-col gap-6">
            {/* KPI skeleton */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <Skeleton className="h-3 w-24 mb-2" />
                <Skeleton className="h-7 w-16" />
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <Skeleton className="h-3 w-24 mb-2" />
                <Skeleton className="h-7 w-12" />
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm col-span-2">
                <Skeleton className="h-3 w-32 mb-2" />
                <Skeleton className="h-6 w-20" />
              </div>
            </div>
            {/* Filter skeleton */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex gap-3">
              <Skeleton className="h-9 flex-1 rounded-lg" />
              <Skeleton className="h-9 flex-1 rounded-lg" />
            </div>
            {/* Map skeleton */}
            <div
              className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm"
              style={{ minHeight: "340px" }}
            >
              <Skeleton className="h-4 w-36 mb-3" />
              <div
                className="rounded-lg bg-slate-100"
                style={{ height: "280px" }}
              >
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="w-10 h-10 border-4 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                    <p className="text-slate-400 text-xs">Memuat peta...</p>
                  </div>
                </div>
              </div>
            </div>
            {/* Table skeleton */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
              <Skeleton className="h-4 w-40 mb-3" />
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 py-2.5 border-b border-slate-50 last:border-0"
                >
                  <Skeleton className="w-6 h-6 rounded" />
                  <Skeleton className="h-3 flex-1" />
                  <Skeleton className="h-5 w-10 rounded" />
                </div>
              ))}
            </div>
          </div>
          {/* Col 2 skeleton */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
            <Skeleton className="h-40 w-full rounded-t-xl" />
            <div className="p-5 space-y-5">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <Skeleton className="h-3 w-32 mb-3" />
                  <Skeleton className="h-36 rounded-lg" />
                </div>
                <div>
                  <Skeleton className="h-3 w-32 mb-3" />
                  <Skeleton className="h-36 rounded-lg" />
                </div>
              </div>
              <Skeleton className="h-3 w-44 mb-3" />
              {[...Array(2)].map((_, i) => (
                <Skeleton key={i} className="h-20 w-full rounded-lg mb-2" />
              ))}
            </div>
          </div>
          {/* Col 3 skeleton */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <Skeleton className="h-5 w-44 mb-1" />
            <Skeleton className="h-3 w-36 mb-4" />
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-24 w-full rounded-lg mb-3" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (err) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-xl border border-red-200 shadow-lg max-w-md text-center">
          <AlertTriangle size={48} className="text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-800 mb-2">
            Koneksi Gagal
          </h2>
          <p className="text-slate-600 mb-4">{err}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Muat Ulang
          </button>
        </div>
      </div>
    );
  }

  const kpiData = dash || {};
  const priorityList = priorities;
  const alerts = anomalies;

  // Real map markers from location coordinates
  const mapMarkers = locations.filter((l) => l.latitude && l.longitude);

  const topicColors = [
    "#3b82f6",
    "#ef4444",
    "#f59e0b",
    "#8b5cf6",
    "#10b981",
    "#6366f1",
    "#ec4899",
    "#14b8a6",
  ];
  const pieData = locDetail?.topic_distribution
    ? Object.entries(locDetail.topic_distribution)
        .map(([n, v], i) => ({ name: n, value: v, color: topicColors[i % 8] }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 5)
    : dash?.topic_distribution
      ? Object.entries(dash.topic_distribution)
          .map(([n, v], i) => ({
            name: n,
            value: v,
            color: topicColors[i % 8],
          }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 5)
      : [{ name: "Kebersihan", value: 50, color: "#3b82f6" }];

  const lineData =
    trends.length > 0
      ? trends.map((d) => ({ name: d.day, keluhan: d.total || d.negatif || 0 }))
      : [{ name: "-", keluhan: 0 }];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100/80 text-slate-800 font-sans p-4 xl:p-6 dashboard-enter">
      {/* Header - Toba Inspired */}
      <div className="mb-8 relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-900 via-blue-800 to-blue-950 p-6 md:p-8 shadow-lg">
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 25% 50%, white 1px, transparent 1px)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl md:text-4xl font-bold text-white tracking-tight">
                TONDI
              </h1>
              <span className="px-2.5 py-0.5 rounded-full bg-white/15 text-white/80 text-[10px] font-semibold uppercase tracking-wider border border-white/10">
                Dashboard
              </span>
            </div>
            <p className="text-blue-200/80 text-sm md:text-base font-light">
              Toba Observatory for Natural-language Destination Intelligence
            </p>
            <p className="text-blue-300/60 text-xs mt-1.5">
              Sistem Pemantauan Reputasi &amp; Integritas Destinasi Danau Toba
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-xs text-blue-200/70 bg-white/10 backdrop-blur-sm px-4 py-2.5 rounded-xl border border-white/10 shadow-sm flex items-center gap-2">
              <Clock size={14} className="text-blue-300" />
              <span className="font-medium text-white/90">AI Pipeline</span>
              <span className="text-blue-300/60">|</span>
              <span>{kpiData.total_reviews?.toLocaleString() || 0} review</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main 3-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ================= COLUMN 1: LEFT ================= */}
        <div className="flex flex-col gap-6">
          {/* KPI Cards - Toba Refined */}
          <div className="grid grid-cols-2 gap-3">
            <div className="group bg-white rounded-xl border border-slate-200/70 shadow-sm hover:shadow-md hover:border-blue-200/50 transition-all duration-300 overflow-hidden">
              <div className="h-1 bg-gradient-to-r from-blue-500 to-cyan-400" />
              <div className="p-4">
                <p className="text-slate-400 text-[11px] font-semibold uppercase tracking-wider mb-2">
                  Total Lokasi
                </p>
                <div className="flex items-end justify-between">
                  <span className="text-2xl font-bold text-slate-900 tabular-nums tracking-tight">
                    {kpiData.total_locations}
                  </span>
                  <div className="p-2 rounded-lg bg-blue-50 text-blue-500 group-hover:bg-blue-100 transition-colors">
                    <MapPin size={18} />
                  </div>
                </div>
              </div>
            </div>
            <div className="group bg-white rounded-xl border border-slate-200/70 shadow-sm hover:shadow-md hover:border-rose-200/50 transition-all duration-300 overflow-hidden">
              <div className="h-1 bg-gradient-to-r from-rose-400 to-orange-400" />
              <div className="p-4">
                <p className="text-slate-400 text-[11px] font-semibold uppercase tracking-wider mb-2">
                  Status Merah
                </p>
                <div className="flex items-end justify-between">
                  <span className="text-2xl font-bold text-rose-600 tabular-nums tracking-tight">
                    {kpiData.red_status || 0}
                  </span>
                  <div className="p-2 rounded-lg bg-rose-50 text-rose-500 group-hover:bg-rose-100 transition-colors">
                    <AlertTriangle size={18} />
                  </div>
                </div>
              </div>
            </div>
            <div className="group bg-white rounded-xl border border-slate-200/70 shadow-sm hover:shadow-md hover:border-amber-200/50 transition-all duration-300 overflow-hidden col-span-2">
              <div className="h-1 bg-gradient-to-r from-amber-400 to-yellow-400" />
              <div className="p-4 flex items-center justify-between">
                <div>
                  <p className="text-slate-400 text-[11px] font-semibold uppercase tracking-wider mb-2">
                    Tren Keluhan Minggu Ini
                  </p>
                  <div className="flex items-center gap-2.5">
                    <span className="text-2xl font-bold text-slate-900 tabular-nums tracking-tight">
                      {kpiData.weekly_trend > 0 ? "+" : ""}
                      {kpiData.weekly_trend || 0}%
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${kpiData.weekly_trend > 0 ? "bg-rose-50 text-rose-600" : kpiData.weekly_trend < 0 ? "bg-emerald-50 text-emerald-600" : "bg-slate-100 text-slate-500"}`}
                    >
                      {kpiData.weekly_trend > 0 ? (
                        <TrendingUp size={12} />
                      ) : kpiData.weekly_trend < 0 ? (
                        <TrendingUp size={12} className="rotate-180" />
                      ) : null}
                      {kpiData.weekly_trend > 0
                        ? "Naik"
                        : kpiData.weekly_trend < 0
                          ? "Turun"
                          : "Stabil"}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1.5">
                    {kpiData.red_status || 0} lokasi merah, {anomalies.length}{" "}
                    anomali
                  </p>
                </div>
                <div className="p-3 rounded-xl bg-gradient-to-br from-amber-50 to-orange-50 text-amber-500">
                  <TrendingUp size={24} />
                </div>
              </div>
            </div>
          </div>

          {/* Filters - Glassmorphism */}
          <div className="bg-white/80 backdrop-blur-sm p-4 rounded-xl border border-slate-200/80 shadow-sm flex gap-3 sticky top-4 z-10">
            <div className="flex-1 relative">
              <select
                value={selectedIssue}
                onChange={(e) => handleIssueChange(e.target.value)}
                className="w-full appearance-none bg-white border border-slate-200 text-sm rounded-lg px-3 py-2.5 pr-8 text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-400 transition-all duration-200"
              >
                <option>Semua Isu</option>
                {filters?.topics?.map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
              <ChevronDown
                size={14}
                className="absolute right-3 top-3.5 text-slate-400 pointer-events-none"
              />
            </div>
            <div className="flex-1 relative">
              <select
                value={selectedRegion}
                onChange={(e) => handleRegionChange(e.target.value)}
                className="w-full appearance-none bg-white border border-slate-200 text-sm rounded-lg px-3 py-2.5 pr-8 text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-400 transition-all duration-200"
              >
                <option>Semua Wilayah</option>
                {filters?.regions?.map((r) => (
                  <option key={r}>{r}</option>
                ))}
              </select>
              <ChevronDown
                size={14}
                className="absolute right-3 top-3.5 text-slate-400 pointer-events-none"
              />
            </div>
          </div>

          {/* Real Leaflet Map - Redesigned */}
          <div className="bg-white rounded-xl border border-slate-200/70 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col">
            <div className="px-4 pt-4 pb-3 flex items-center justify-between border-b border-slate-100">
              <h2 className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-2">
                <MapPin size={14} className="text-blue-500" /> Peta Persebaran
                Isu
              </h2>
              <div className="flex gap-3 text-[10px] text-slate-500">
                <div className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-white shadow-sm" />
                  <span className="font-medium text-slate-600">Aman</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-amber-400 ring-2 ring-white shadow-sm" />
                  <span className="font-medium text-slate-600">Waspada</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-3.5 h-3.5 rounded-full bg-rose-500 ring-2 ring-white shadow-sm" />
                  <span className="font-medium text-slate-600">Kritis</span>
                </div>
              </div>
            </div>
            <div
              className="m-3 rounded-lg border border-slate-100 overflow-hidden z-0 relative"
              style={{ height: "340px", minHeight: "340px" }}
            >
              {mapMarkers.length > 0 && (
                <MapContainer
                  center={[2.5839, 98.7816]}
                  zoom={9}
                  className="w-full h-full"
                  scrollWheelZoom={true}
                >
                  <MapFlyController mapRef={mapRef} />
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />
                  {mapMarkers.map((loc, idx) => (
                    <Marker
                      key={idx}
                      position={[loc.latitude, loc.longitude]}
                      icon={L.divIcon({
                        className: "custom-marker",
                        html: `<div style="
                          width: ${loc.status === "red" ? "18" : loc.status === "yellow" ? "14" : "12"}px;
                          height: ${loc.status === "red" ? "18" : loc.status === "yellow" ? "14" : "12"}px;
                          border-radius: 50%;
                          background: ${loc.status === "red" ? "#ef4444" : loc.status === "yellow" ? "#f59e0b" : "#10b981"};
                          border: 3px solid white;
                          box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                          cursor: pointer;
                        "
                        ></div>`,
                        iconSize: [22, 22],
                        iconAnchor: [11, 11],
                      })}
                    >
                      <Popup>
                        <div className="text-sm" style={{ minWidth: "200px" }}>
                          {getImageUrl(loc.name) && (
                            <img
                              src={getImageUrl(loc.name)}
                              alt={loc.name}
                              style={{
                                width: "100%",
                                height: "90px",
                                objectFit: "cover",
                                borderRadius: "6px",
                                marginBottom: "6px",
                              }}
                            />
                          )}
                          <h3 className="font-bold text-slate-900 text-base mb-1">
                            {loc.name}
                          </h3>
                          <div className="flex items-center gap-2 mb-2">
                            <span
                              style={{
                                display: "inline-block",
                                padding: "2px 8px",
                                borderRadius: "999px",
                                fontSize: "11px",
                                fontWeight: 600,
                                background:
                                  loc.status === "red"
                                    ? "#fef2f2"
                                    : loc.status === "yellow"
                                      ? "#fffbeb"
                                      : "#ecfdf5",
                                color:
                                  loc.status === "red"
                                    ? "#dc2626"
                                    : loc.status === "yellow"
                                      ? "#d97706"
                                      : "#059669",
                              }}
                            >
                              {loc.status === "red"
                                ? "Kritis"
                                : loc.status === "yellow"
                                  ? "Waspada"
                                  : "Aman"}
                            </span>
                            <span className="text-slate-400 text-xs">
                              {loc.total_reviews} review
                            </span>
                          </div>
                          <div className="flex gap-2 text-xs text-slate-500 mb-2">
                            <span>
                              Rating: {loc.rating?.toFixed(1) || "-"}/5
                            </span>
                            <span>|</span>
                            <span className="text-red-500">
                              {loc.negatif} negatif
                            </span>
                          </div>
                          {loc.region && (
                            <div className="text-xs text-slate-400 mb-2">
                              Wilayah: {loc.region}
                            </div>
                          )}
                          <button
                            onClick={() => clickLoc(loc.name)}
                            style={{
                              width: "100%",
                              padding: "5px 10px",
                              background: "#2563eb",
                              color: "white",
                              border: "none",
                              borderRadius: "6px",
                              fontSize: "11px",
                              fontWeight: 600,
                              cursor: "pointer",
                            }}
                          >
                            Lihat Detail
                          </button>
                        </div>
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              )}
            </div>
          </div>

          {/* Priority List Table - Refined */}
          <div className="bg-white rounded-xl border border-slate-200/70 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col">
            <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Daftar Prioritas Lokasi
                </h2>
              </div>
              <span className="text-[10px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                Top {priorityList.length}
              </span>
            </div>
            <div
              className="overflow-x-auto"
              style={{ maxHeight: "280px", overflowY: "auto" }}
            >
              <table className="w-full text-left text-xs whitespace-nowrap">
                <thead className="bg-slate-50/80 text-slate-400 font-semibold sticky top-0 backdrop-blur-sm">
                  <tr>
                    <th className="px-3 py-2.5 text-[11px] uppercase tracking-wider">
                      Nama Lokasi
                    </th>
                    <th className="px-3 py-2.5 text-center text-[11px] uppercase tracking-wider">
                      Skor
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100/80">
                  {priorityList.map((item, idx) => (
                    <tr
                      key={idx}
                      className={
                        "hover:bg-blue-50/50 transition-all duration-200 cursor-pointer group/row " +
                        (selLoc === item.name ? "bg-blue-50/80 shadow-sm" : "")
                      }
                      onClick={() => clickLoc(item.name)}
                    >
                      <td className="px-3 py-2.5">
                        <div className="flex items-center gap-2.5">
                          <div
                            className={`w-2 h-2 rounded-full flex-shrink-0 ring-2 ring-white shadow-sm transition-transform group-hover/row:scale-125 ${
                              item.status === "Merah"
                                ? "bg-rose-500"
                                : item.status === "Kuning"
                                  ? "bg-amber-400"
                                  : "bg-emerald-500"
                            }`}
                          />
                          {getImageUrl(item.name) ? (
                            <img
                              src={getImageUrl(item.name)}
                              alt={item.name}
                              className="w-6 h-6 rounded-md object-cover flex-shrink-0 border border-slate-200/80"
                            />
                          ) : (
                            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-50 to-blue-100 flex-shrink-0 flex items-center justify-center border border-slate-200/80">
                              <MapPin size={10} className="text-blue-400" />
                            </div>
                          )}
                          <span className="font-medium text-slate-700 truncate max-w-[140px] group-hover/row:text-blue-700 transition-colors">
                            {item.name}
                          </span>
                        </div>
                      </td>
                      <td className="px-3 py-2.5 text-center">
                        <div
                          className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md font-bold text-[11px] tabular-nums ${
                          item.score >= 70 ? 'bg-rose-50 text-rose-700 ring-1 ring-rose-200/50' : 
                          item.score >= 60 ? 'bg-amber-50 text-amber-700 ring-1 ring-amber-200/50' : 
                          'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200/50'
                        }"
                        >
                          {item.score}
                          <span
                            className={
                              "text-[9px] font-medium " +
                              (item.status === "Merah"
                                ? "text-rose-400"
                                : item.status === "Kuning"
                                  ? "text-amber-400"
                                  : "text-emerald-400")
                            }
                          >
                            {item.status}
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* ================= COLUMN 2: MIDDLE - Redesigned ================= */}
        <div className="flex flex-col gap-6">
          <div className="group bg-white rounded-xl border border-slate-200/70 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden">
            {/* Header: Location Detail with refined overlay */}
            <div className="relative h-44 bg-slate-200 overflow-hidden">
              {selLoc && getImageUrl(selLoc) ? (
                <img
                  src={getImageUrl(selLoc)}
                  alt={selLoc}
                  className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
              ) : (
                <div className="absolute inset-0 bg-gradient-to-br from-blue-700 via-blue-600 to-indigo-800" />
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />
              <div className="absolute inset-0 bg-gradient-to-r from-black/20 to-transparent" />
              {/* Decorative pattern */}
              <div
                className="absolute inset-0 opacity-[0.04]"
                style={{
                  backgroundImage:
                    "radial-gradient(circle at 50% 0%, white 1px, transparent 1px)",
                  backgroundSize: "20px 20px",
                }}
              />

              <div className="absolute bottom-0 left-0 right-0 p-5">
                <div className="flex justify-between items-end w-full">
                  <div>
                    <h2 className="text-2xl font-bold text-white drop-shadow-lg tracking-tight">
                      {selLoc || "Pilih Lokasi"}
                    </h2>
                    <div className="flex items-center gap-2 mt-1.5">
                      <span className="text-blue-200/80 text-xs flex items-center gap-1">
                        <MapPin size={12} />{" "}
                        {locDetail?.category ||
                          "Klik lokasi di tabel prioritas atau peta"}
                      </span>
                      {locDetail && (
                        <>
                          <span className="text-blue-200/40">|</span>
                          <span className="text-blue-200/80 text-xs">
                            {locDetail.total_reviews} review
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  {locDetail && (
                    <div className="flex bg-black/40 backdrop-blur-md px-3 py-2 rounded-xl items-center gap-1.5 border border-white/10 shadow-lg">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          size={14}
                          className={
                            star <= Math.round(locDetail.rating || 2)
                              ? "text-amber-300 fill-amber-300 drop-shadow-sm"
                              : "text-white/30"
                          }
                        />
                      ))}
                      <span className="text-white text-xs font-bold tabular-nums ml-0.5">
                        {(locDetail.rating || 0).toFixed(1)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="p-5 flex flex-col gap-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Pie Chart */}
                <div className="flex flex-col">
                  <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-gradient-to-br from-blue-400 to-cyan-400" />
                    Distribusi Topik Isu
                  </h3>
                  <div className="h-40 w-full relative">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={pieData}
                          cx="50%"
                          cy="50%"
                          innerRadius={38}
                          outerRadius={62}
                          paddingAngle={3}
                          dataKey="value"
                        >
                          {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip
                          contentStyle={{
                            borderRadius: "10px",
                            fontSize: "12px",
                            border: "1px solid #e2e8f0",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex flex-wrap gap-x-3 gap-y-1.5 justify-center mt-2.5">
                    {pieData.map((item, i) => (
                      <div
                        key={item.name}
                        className={`flex items-center gap-1.5 text-[10px] font-medium animate-fadeIn`}
                        style={{ animationDelay: `${i * 80}ms` }}
                      >
                        <div
                          className="w-2 h-2 rounded-full ring-1 ring-white shadow-sm"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-slate-600">{item.name}</span>
                        <span className="text-slate-400 tabular-nums">
                          {item.value}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Line Chart - Refined */}
                <div className="flex flex-col">
                  <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-gradient-to-br from-rose-400 to-orange-400" />
                    Tren Keluhan (7 Hari)
                  </h3>
                  <div className="h-40 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={lineData}>
                        <CartesianGrid
                          strokeDasharray="3 3"
                          vertical={false}
                          stroke="#f1f5f9"
                        />
                        <XAxis
                          dataKey="name"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 10, fill: "#94a3b8" }}
                        />
                        <YAxis
                          axisLine={false}
                          tickLine={false}
                          tick={{ fontSize: 10, fill: "#94a3b8" }}
                          width={25}
                        />
                        <Tooltip
                          contentStyle={{
                            borderRadius: "10px",
                            fontSize: "12px",
                            border: "1px solid #e2e8f0",
                            boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                          }}
                        />
                        <defs>
                          <linearGradient
                            id="lineGrad"
                            x1="0"
                            y1="0"
                            x2="1"
                            y2="0"
                          >
                            <stop offset="0%" stopColor="#f43f5e" />
                            <stop offset="100%" stopColor="#f97316" />
                          </linearGradient>
                        </defs>
                        <Line
                          type="monotone"
                          dataKey="keluhan"
                          stroke="url(#lineGrad)"
                          strokeWidth={2.5}
                          dot={{
                            r: 2.5,
                            fill: "#f43f5e",
                            strokeWidth: 2,
                            stroke: "#fff",
                          }}
                          activeDot={{
                            r: 4.5,
                            fill: "#f43f5e",
                            strokeWidth: 2,
                            stroke: "#fff",
                          }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Reviews Section - Refined cards */}
              <div className="border-t border-slate-100 pt-5">
                <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <MessageSquare size={13} className="text-slate-400" /> Kutipan
                  Ulasan Terkait
                </h3>
                <div className="flex flex-col gap-2.5 max-h-[240px] overflow-y-auto pr-1 custom-scrollbar">
                  {selLoc && recommendations.length > 0
                    ? getRelevantReviews().length > 0
                      ? getRelevantReviews().map((review, idx) => (
                          <ReviewCard key={idx} review={review} />
                        ))
                      : (locDetail?.recent_reviews || reviews)
                          .slice(0, 3)
                          .map((review, idx) => (
                            <ReviewCard key={idx} review={review} />
                          ))
                    : reviews
                        .slice(0, 3)
                        .map((review, idx) => (
                          <ReviewCard key={idx} review={review} />
                        ))}
                  {(!selLoc || recommendations.length === 0) &&
                    reviews.length === 0 && (
                      <p className="text-sm text-slate-400 italic text-center py-6">
                        Pilih lokasi untuk melihat ulasan terkait.
                      </p>
                    )}
                </div>
              </div>

              {/* Recommendations - Refined */}
              <div className="bg-gradient-to-br from-blue-50/80 to-indigo-50/40 p-5 rounded-xl border border-blue-100/80">
                <h3 className="text-[11px] font-bold text-blue-800 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <CheckCircle2 size={14} className="text-blue-600" />{" "}
                  Rekomendasi Tindakan
                </h3>
                {recommendations.length > 0 ? (
                  <ul className="space-y-3">
                    {recommendations.map((r, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-3 bg-white/70 p-3.5 rounded-xl border border-blue-100/60 shadow-sm"
                      >
                        <span
                          className={
                            "w-6 h-6 flex-shrink-0 rounded-lg flex items-center justify-center text-xs font-bold mt-0.5 text-white shadow-sm " +
                            (r.priority === "Kritis"
                              ? "bg-gradient-to-br from-rose-500 to-red-600"
                              : r.priority === "Tinggi"
                                ? "bg-gradient-to-br from-orange-400 to-amber-600"
                                : "bg-gradient-to-br from-blue-500 to-indigo-600")
                          }
                        >
                          {i + 1}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-slate-800">
                            {r.action}
                          </p>
                          <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                            {r.reason}
                          </p>
                          <span
                            className={
                              "inline-block text-[10px] font-semibold px-2 py-0.5 rounded-full mt-2 " +
                              (r.priority === "Kritis"
                                ? "bg-rose-50 text-rose-700 ring-1 ring-rose-200/50"
                                : r.priority === "Tinggi"
                                  ? "bg-amber-50 text-amber-700 ring-1 ring-amber-200/50"
                                  : "bg-blue-50 text-blue-700 ring-1 ring-blue-200/50")
                            }
                          >
                            {r.priority}
                          </span>
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-center py-6">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mx-auto mb-2">
                      <CheckCircle2 size={20} className="text-blue-400" />
                    </div>
                    <p className="text-sm text-slate-500">
                      Pilih lokasi untuk melihat rekomendasi.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ================= COLUMN 3: RIGHT - Redesigned ================= */}
        <div className="flex flex-col gap-6">
          <div className="group bg-white rounded-xl border border-slate-200/70 shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col h-full">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center gap-3 bg-gradient-to-r from-rose-50/50 to-amber-50/30">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-rose-100 to-rose-50 flex items-center justify-center shadow-sm">
                <AlertTriangle size={18} className="text-rose-500" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900">
                  Notifikasi Anomali
                </h2>
                <p className="text-[11px] text-slate-500">
                  Lonjakan keluhan mendadak terdeteksi
                </p>
              </div>
            </div>

            <div className="p-4 flex-1 flex flex-col gap-3">
              {alerts.map((alert, idx) => (
                <div
                  key={idx}
                  className="relative bg-white border border-slate-200/80 rounded-xl p-3.5 hover:border-slate-300/80 transition-all duration-200 shadow-sm hover:shadow-md group/alert cursor-pointer overflow-hidden"
                  onClick={() => clickLoc(alert.location)}
                >
                  {/* Gradient left accent bar */}
                  <div
                    className={`absolute left-0 top-0 bottom-0 w-[3px] rounded-l-xl bg-gradient-to-b ${
                      alert.color && alert.color.includes("red")
                        ? "from-rose-500 to-red-400"
                        : alert.color && alert.color.includes("orange")
                          ? "from-orange-400 to-amber-400"
                          : "from-amber-400 to-yellow-400"
                    }`}
                  />
                  <div className="pl-4">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] font-semibold text-slate-400 flex items-center gap-1.5 uppercase tracking-wider">
                        Z-Score:{" "}
                        <span className="font-bold tabular-nums text-slate-600">
                          {alert.z_score}
                        </span>
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1
                        ${
                          alert.status === "Kritis"
                            ? "bg-rose-50 text-rose-700 ring-1 ring-rose-200/50"
                            : alert.status === "Tinggi"
                              ? "bg-amber-50 text-amber-700 ring-1 ring-amber-200/50"
                              : "bg-orange-50 text-orange-700 ring-1 ring-orange-200/50"
                        }
                      `}
                      >
                        {alert.status}
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-slate-800 mb-2 group-hover/alert:text-blue-700 transition-colors">
                      {alert.location}
                    </h4>
                    <div className="flex items-center justify-between">
                      <div className="inline-flex items-center gap-1.5 bg-slate-100/80 text-slate-600 text-[10px] font-semibold px-2.5 py-1 rounded-lg">
                        <AlertTriangle size={10} className="text-slate-400" />
                        Isu: {alert.issue}
                      </div>
                      <div className="text-right">
                        <div className="text-[9px] text-slate-400 font-medium mb-0.5">
                          Lonjakan
                        </div>
                        <div className="text-sm font-bold text-rose-600 flex items-center gap-1 tabular-nums">
                          <TrendingUp size={13} /> {alert.surge}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {alerts.length === 0 && (
                <div className="text-center py-10">
                  <div className="w-14 h-14 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-3 ring-1 ring-emerald-200/50">
                    <CheckCircle2 size={28} className="text-emerald-400" />
                  </div>
                  <p className="text-sm font-medium text-slate-600">
                    Semua Lokasi Normal
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Tidak ada anomali terdeteksi
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style
        dangerouslySetInnerHTML={{
          __html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #f1f5f9; 
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1; 
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #94a3b8; 
        }
        .custom-marker div { transition: transform 0.2s !important; }
        .custom-marker div:hover { transform: scale(1.3) !important; }
        .dashboard-enter { animation: dashEnter 0.45s ease-out both; }
        .animate-fadeIn { animation: fadeIn 0.4s ease-out both; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes dashEnter {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `,
        }}
      />
    </div>
  );
}
