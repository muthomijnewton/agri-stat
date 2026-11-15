"""14-day demand models. Weather regressors lag 21 days; demand regressors lag 14 days to avoid hindsight.

No imputation of unrecorded sales. Model artifacts are JSON/text, never pickle.
"""
import hashlib
import json
import numpy as np
import pandas as pd

FEATURES = ['weekday', 'month', 'demand_lag14', 'demand_mean7', 'rain7', 'rain14', 'soil', 'route_rain_3d_mm']
QUANTILES = (.1, .5, .9)
MIN_DAYS = 120


def features(history, weather, dates):
    index = pd.date_range(history.index.min(), max(dates), freq='D')
    y = history.reindex(index)
    w = weather.reindex(index)
    x = pd.DataFrame(index=index)
    x['weekday'] = index.day_of_week
    x['month'] = index.month
    x['demand_lag14'] = y.shift(14)
    x['demand_mean7'] = y.rolling(7, min_periods=7).mean().shift(14)
    x['rain7'] = w.rainfall_mm.rolling(7, min_periods=7).sum().shift(21)
    x['rain14'] = w.rainfall_mm.rolling(14, min_periods=14).sum().shift(21)
    x['soil'] = w.soil_moisture.rolling(7, min_periods=7).mean().shift(21)
    x['route_rain_3d_mm'] = w.route_rainfall_mm.rolling(3, min_periods=3).sum().shift(21)
    return x.reindex(dates)[FEATURES]


def scores(actual, predictions):
    y = np.asarray(actual, dtype=float)
    p = np.asarray(predictions, dtype=float)
    errors = y[:, None] - p
    losses = np.maximum(np.array(QUANTILES)*errors, (np.array(QUANTILES)-1)*errors)
    nonzero = y > 0
    return {'mae': float(np.mean(np.abs(y-p[:,1]))), 'pinball_loss': float(losses.mean()),
        'pinball_by_quantile': dict(zip(('p10','p50','p90'), map(float, losses.mean(axis=0)))),
        'mape_nonzero_percent': float(np.mean(np.abs((y[nonzero]-p[nonzero,1])/y[nonzero]))*100) if nonzero.any() else None,
        'mape_excluded_zero_days': int((~nonzero).sum()),
        'coverage_p10_p90': float(np.mean((y >= p[:,0]) & (y <= p[:,2])))}


def ordered(predictions):
    result = np.sort(np.maximum(0, np.asarray(predictions, dtype=float)), axis=1)
    if not np.isfinite(result).all():
        raise ValueError('Model returned non-finite predictions')
    return result


def fit_predict(name, x, y, future):
    if name == 'lightgbm':
        import lightgbm as lgb
        models = []
        for quantile in QUANTILES:
            model = lgb.train({'objective': 'quantile', 'alpha': quantile,
                'num_leaves': 7, 'min_data_in_leaf': 10, 'learning_rate': .05,
                'seed': 42, 'num_threads': 1, 'verbosity': -1,
                'deterministic': True, 'force_col_wise': True}, lgb.Dataset(x, label=y), num_boost_round=100)
            models.append(model)
        return ordered(np.column_stack([m.predict(future, num_threads=1) for m in models])), {
            'format': 'lightgbm-text', 'models': [m.model_to_string() for m in models], 'library_version': lgb.__version__}
    from prophet import Prophet
    from prophet.serialize import model_to_json
    model = Prophet(interval_width=.8, yearly_seasonality=False, daily_seasonality=False,
                    weekly_seasonality=True, uncertainty_samples=1000)
    # Calendar seasonality belongs to Prophet; the remaining regressors are known 14 days ahead.
    regressors = FEATURES[2:]
    for column in regressors:
        model.add_regressor(column)
    data = x[regressors].copy(); data['ds'] = x.index; data['y'] = np.asarray(y)
    model.fit(data, seed=42)
    frame = future[regressors].copy(); frame['ds'] = future.index
    # Prophet uncertainty uses numpy's RNG; preserve the caller's state.
    state = np.random.get_state()
    try:
        np.random.seed(42)
        prediction = model.predict(frame)
    finally:
        np.random.set_state(state)
    import prophet
    return ordered(prediction[['yhat_lower','yhat','yhat_upper']].values), {
        'format': 'prophet-json', 'model': model_to_json(model), 'library_version': prophet.__version__}


def train_validate(history, weather):
    """Returns candidate evaluation; promotion requires beating a seasonal baseline."""
    history = history.sort_index().astype(float)
    expected = pd.date_range(history.index.min(), history.index.max(), freq='D')
    if len(history) < MIN_DAYS or not history.index.equals(expected) or not history.index.is_unique:
        raise ValueError('Need at least 120 consecutive confirmed daily totals; missing days are not zero sales')
    if not np.isfinite(history.values).all() or (history < 0).any() or history.sum() <= 0:
        raise ValueError('Demand history must be finite, nonnegative and contain actual sales')
    x = features(history, weather, history.index)
    valid = x.notna().all(axis=1)
    # Only the initial rolling-window warmup may be missing.
    if not valid.iloc[34:].all() or not np.isfinite(x.iloc[34:].values).all():
        raise ValueError('Historical rainfall, soil moisture or route weather is incomplete')
    x = x.iloc[34:]; y = history.reindex(x.index)
    train_x, test_x = x.iloc[:-14], x.iloc[-14:]
    train_y, test_y = y.iloc[:-14], y.iloc[-14:]
    cutoff = train_y.index[-1]
    baseline_history = history.loc[:cutoff]
    point = np.resize(baseline_history.iloc[-7:].values, 14)
    residuals = (baseline_history-baseline_history.shift(7)).dropna().values
    baseline = ordered(point[:,None] + np.quantile(residuals, QUANTILES)[None,:])
    baseline_metrics = scores(test_y, baseline)
    reports, candidates = {}, {}
    for name in ('lightgbm', 'prophet'):
        try:
            predictions, _ = fit_predict(name, train_x, train_y, test_x)
            metrics = scores(test_y, predictions)
            reports[name] = {'metrics': metrics}
            if metrics['mae'] <= baseline_metrics['mae'] and metrics['pinball_loss'] <= baseline_metrics['pinball_loss']:
                candidates[name] = metrics['pinball_loss']
        except (ImportError, ValueError, RuntimeError) as exc:
            reports[name] = {'error': str(exc)[:300]}
    result = {'model_version': 'farm-demand-v1', 'features': FEATURES, 'demand_feature_lag_days': 14, 'weather_feature_lag_days': 21,
        'history_days': len(history), 'history_start': str(history.index[0].date()), 'history_end': str(history.index[-1].date()),
        'holdout_start': str(test_y.index[0].date()), 'holdout_end': str(test_y.index[-1].date()),
        'baseline': baseline_metrics, 'candidates': reports,
        'data_sha256': hashlib.sha256((history.to_csv()+weather.to_csv()).encode()).hexdigest(),
        'input_snapshot': {'demand_csv': history.to_csv(), 'weather_csv': weather.to_csv()},
        'status': 'rejected', 'message': 'Neither model beat the weekly baseline on both MAE and pinball loss.'}
    if not candidates:
        return result
    winner = min(candidates, key=candidates.get)
    future_dates = pd.date_range(history.index[-1]+pd.Timedelta(days=1), periods=14)
    future_x = features(history, weather, future_dates)
    if future_x.isna().any().any():
        raise ValueError('Weather history is incomplete for the forecast horizon')
    predictions, artifact = fit_predict(winner, x, y, future_x)
    result.update(status='validated', selected_model=winner, artifact=artifact,
        message='Passed one 14-day holdout against a weekly baseline; monitor accuracy before relying on it.',
        demand_std=float(history.std(ddof=1)), forecasts=[{'date': str(day.date()),
        'p10': float(p[0]), 'p50': float(p[1]), 'p90': float(p[2])} for day,p in zip(future_dates,predictions)])
    # JSON serialization is checked here, before persistence.
    json.dumps(result, allow_nan=False)
    return result
