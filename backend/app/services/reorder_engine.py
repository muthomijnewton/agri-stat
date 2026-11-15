"""Transparent planning heuristics, not calibrated travel-time predictions."""
import math


def calculate_plan(*, base_lead_days, unpaved_ratio, unknown_ratio, rain_3d_mm,
                   daily_demand, demand_std, net_stock, shelf_life_days=None,
                   temp_max_c=None, optimal_temp_max_c=None, review_days=7, z=1.645):
    values = [base_lead_days,unpaved_ratio,unknown_ratio,rain_3d_mm,daily_demand,demand_std,net_stock,review_days,z]
    if any(not math.isfinite(v) or v < 0 for v in values) or base_lead_days <= 0:
        raise ValueError('Planning inputs must be finite and nonnegative; lead time must be positive')
    if unpaved_ratio + unknown_ratio > 1.000001:
        raise ValueError('Road surface ratios are invalid')
    if shelf_life_days is not None and (not math.isfinite(shelf_life_days) or shelf_life_days <= 0):
        raise ValueError('Shelf life must be positive when supplied')
    if any(v is not None and not math.isfinite(v) for v in (temp_max_c,optimal_temp_max_c)):
        raise ValueError('Temperature must be finite')
    rsi = min(1, max(0, rain_3d_mm-15)/35)
    # Unknown surfaces remain visible; conservatively treat them as unpaved for planning.
    effective_unpaved = min(1, unpaved_ratio+unknown_ratio)
    lead = base_lead_days*(1+1.5*effective_unpaved*rsi)
    safety = z*demand_std*math.sqrt(lead)
    rop = daily_demand*lead+safety
    target = daily_demand*(lead+review_days)+safety
    # Existing inventory consumes some of the post-arrival shelf-life capacity too.
    stock_at_arrival = max(0,net_stock-daily_demand*lead)
    cap = max(0,daily_demand*max(0,shelf_life_days-lead)-stock_at_arrival) if shelf_life_days is not None else None
    need = max(0,target-net_stock) if net_stock <= rop else 0
    order = min(need,cap) if cap is not None else need
    reasons = []
    if unknown_ratio > 0: reasons.append('Unknown road surfaces treated conservatively as unpaved')
    high = False
    if shelf_life_days is not None and lead > .5*shelf_life_days:
        high=True; reasons.append('Transit consumes more than half the stated shelf life')
    if optimal_temp_max_c is not None and temp_max_c is not None and temp_max_c > optimal_temp_max_c:
        high=True; reasons.append('Forecast temperature exceeds the product limit')
    if shelf_life_days is not None and lead >= shelf_life_days:
        order=0; reasons.append('Produce would reach its shelf-life limit before arrival')
    return {'rain_severity_index':rsi,'adjusted_lead_time_days':lead,'safety_stock':safety,
        'reorder_point':rop,'shelf_life_order_cap':cap,'recommended_order_quantity':max(0,order),
        'risk_level':'HIGH' if high else 'MODERATE' if rsi*effective_unpaved > .2 else 'LOW',
        'reasons':reasons,'assumptions':{'alpha':1.5,'z':z,'review_days':review_days,
        'method':'Uncalibrated blueprint heuristic; shelf life is measured from dispatch; no outstanding purchase orders included'}}
