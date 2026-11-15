"""Profile actual routed node pairs; unrelated nearby roads are excluded."""
import os

from app.models.foundation import Location, utcnow
from app.services.external_data import fetch_json

PAVED = {"asphalt", "paved", "concrete", "concrete:plates", "concrete:lanes", "paving_stones", "sett"}
UNPAVED = {"unpaved", "gravel", "fine_gravel", "dirt", "earth", "ground", "murram", "sand", "mud", "compacted"}


def surface_profile(legs, ways):
    edges = {}
    for way in ways:
        nodes = way.get("nodes", [])
        tag = way.get("tags", {}).get("surface", "").lower()
        surface = "unpaved" if tag in UNPAVED else "paved" if tag in PAVED else "unknown"
        for a, b in zip(nodes, nodes[1:]):
            edges.setdefault(tuple(sorted((a, b))), set()).add(surface)
    totals = {"unpaved": 0.0, "paved": 0.0, "unknown": 0.0}
    for leg in legs:
        annotation = leg.get("annotation", {})
        nodes, distances = annotation.get("nodes", []), annotation.get("distance", [])
        if len(nodes) != len(distances) + 1:
            raise ValueError("Routing provider returned incomplete node/distance annotations")
        for a, b, distance in zip(nodes, nodes[1:], distances):
            classifications = edges.get(tuple(sorted((a, b))), {"unknown"})
            surface = next(iter(classifications)) if len(classifications) == 1 else "unknown"
            if distance < 0:
                raise ValueError("Invalid route segment distance")
            totals[surface] += distance
    total = sum(totals.values())
    if total <= 0:
        raise ValueError("Route has no measurable segments")
    return {"unpaved_ratio": totals["unpaved"] / total,
            "unknown_surface_ratio": totals["unknown"] / total}


def inspect_route(db, route, *, fetch=fetch_json):
    origin = db.get(Location, route.origin_location_id)
    destination = db.get(Location, route.dest_location_id)
    if any(location is None or location.organization_id != route.organization_id for location in (origin, destination)):
        raise ValueError("Route endpoints must belong to the route organization")
    if any(location.latitude is None or location.longitude is None for location in (origin, destination)):
        raise ValueError("Both route endpoints need verified coordinates")
    coordinates = f"{origin.longitude},{origin.latitude};{destination.longitude},{destination.latitude}"
    base = os.getenv("OSRM_URL", "https://router.project-osrm.org").rstrip("/")
    result = fetch(f"{base}/route/v1/driving/{coordinates}",
                   params={"overview": "full", "geometries": "geojson", "annotations": "nodes,distance"})
    if result.get("code") != "Ok" or not result.get("routes"):
        raise ValueError("No drivable route found")
    selected = result["routes"][0]
    node_ids = sorted({node for leg in selected["legs"] for node in leg["annotation"]["nodes"]})
    if len(node_ids) > 20000:
        raise ValueError("Route exceeds the 20,000-node inspection limit")
    ways = {}
    for offset in range(0, len(node_ids), 200):
        ids = ",".join(str(int(node)) for node in node_ids[offset:offset + 200])
        query = f'[out:json][timeout:45];node(id:{ids});way(bn)["highway"];out body;'
        data = fetch(os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter"), data={"data": query})
        if data.get("remark"):
            raise ValueError("Overpass returned an incomplete result; retry later")
        for way in data.get("elements", []):
            if way.get("type") == "way":
                ways[way["id"]] = way
    profile = surface_profile(selected["legs"], ways.values())
    route.total_distance_km = selected["distance"] / 1000
    route.route_geometry = selected["geometry"]
    for key, value in profile.items():
        setattr(route, key, value)
    # Surface profiling is Phase 1. Weather-adjusted lead time is Phase 2.
    route.current_risk_level = "UNKNOWN"
    route.inspected_at = utcnow()
    db.flush()
    return {"route_id": route.id, "distance_km": float(route.total_distance_km), **profile}
