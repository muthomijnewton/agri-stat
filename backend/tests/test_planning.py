"""Isolated test fixtures only. No test data enters the operational database."""
from datetime import timedelta
from uuid import uuid4
import numpy as np
import pandas as pd
import pytest
from app.models.foundation import SupplyRoute, Organization
from app.models.planning import ForecastRun, DemandDay
from app.services.demand_model import features, scores, train_validate, fit_predict
from app.services.reorder_engine import calculate_plan
from app.services.planning_service import local_today, demand_history
from tests.test_farm_sales import farm, tomatoes


def inputs():
    return dict(base_lead_days=2,unpaved_ratio=.6,unknown_ratio=.1,rain_3d_mm=50,
        daily_demand=10,demand_std=2,net_stock=0,shelf_life_days=7)


def test_weather_delay_and_nonnegative_shelf_cap():
    plan=calculate_plan(**inputs())
    assert plan['adjusted_lead_time_days']==pytest.approx(4.1)
    assert plan['risk_level']=='HIGH'
    assert plan['recommended_order_quantity']==pytest.approx(29)
    values=inputs();values['shelf_life_days']=3
    assert calculate_plan(**values)['recommended_order_quantity']==0
    values=inputs();values['net_stock']=10000
    assert calculate_plan(**values)['recommended_order_quantity']==0


def test_existing_stock_consumes_shelf_capacity_and_heat_guard():
    values=inputs();values.update(net_stock=45,temp_max_c=35,optimal_temp_max_c=25)
    plan=calculate_plan(**values)
    assert plan['shelf_life_order_cap']==pytest.approx(25)
    assert plan['risk_level']=='HIGH'
    assert any('temperature' in x for x in plan['reasons'])


@pytest.mark.parametrize('field,value',[('rain_3d_mm',float('nan')),('net_stock',-1),('base_lead_days',0),('unknown_ratio',.9)])
def test_invalid_plan_inputs(field,value):
    values=inputs();values[field]=value
    with pytest.raises(ValueError):calculate_plan(**values)


def series():
    dates=pd.date_range('2025-01-01',periods=160)
    history=pd.Series(20+np.sin(np.arange(160)*2*np.pi/7)*5,index=dates,name='quantity')
    weather=pd.DataFrame({'rainfall_mm':2.,'soil_moisture':.25,'route_rainfall_mm':3.},index=dates)
    return history,weather


def test_holdout_features_do_not_leak_hidden_sales_or_weather():
    history,weather=series();dates=history.index[-14:]
    original=features(history,weather,dates)
    history.iloc[-14:]=99999;weather.iloc[-14:]=99999
    pd.testing.assert_frame_equal(original,features(history,weather,dates))


def test_scores_with_zero_demand_are_finite():
    metrics=scores([0,10],[[0,0,1],[8,10,12]])
    assert metrics['mape_excluded_zero_days']==1 and metrics['mape_nonzero_percent']==0
    assert metrics['coverage_p10_p90']==1


def test_missing_days_and_missing_weather_block_models():
    history,weather=series()
    with pytest.raises(ValueError,match='consecutive'):train_validate(history.drop(history.index[50]),weather)
    weather.iloc[80,0]=np.nan
    with pytest.raises(ValueError,match='incomplete'):train_validate(history,weather)


def test_real_model_libraries_train_and_return_ordered_intervals():
    history,weather=series();x=features(history,weather,history.index).iloc[34:]
    for name in ('lightgbm','prophet'):
        prediction,artifact=fit_predict(name,x.iloc[:-14],history.reindex(x.index).iloc[:-14],x.iloc[-14:])
        assert prediction.shape==(14,3)
        assert (prediction[:,0]>=0).all() and (np.diff(prediction,axis=1)>=0).all()
        assert artifact['library_version']


def test_training_returns_holdout_evidence():
    history,weather=series();result=train_validate(history,weather)
    assert result['holdout_start']==str(history.index[-14].date())
    assert set(result['candidates'])=={'lightgbm','prophet'}
    assert all('metrics' in r for r in result['candidates'].values())
    assert len(result['data_sha256'])==64
    if result['status']=='validated':
        assert len(result['forecasts'])==14 and result['artifact']
        metrics=result['candidates'][result['selected_model']]['metrics']
        assert metrics['mae']<=result['baseline']['mae'] and metrics['pinball_loss']<=result['baseline']['pinball_loss']


def test_confirm_daily_zero_and_duplicate(client,db,farm,tomatoes):
    data={'location_id':farm.id,'product_id':tomatoes.id,'date':str(local_today()-timedelta(days=1)),
          'stockout':False,'source':'Daily sales checked','use_sales_ledger':True}
    response=client.post('/api/v1/planning/demand-days',json=data)
    assert response.status_code==201,response.text
    assert float(response.json()['quantity'])==0
    assert client.post('/api/v1/planning/demand-days',json=data).status_code==409
    data['date']=str(local_today())
    assert client.post('/api/v1/planning/demand-days',json=data).status_code==422


def test_historical_totals_do_not_create_stock_or_sales(client,db,farm,tomatoes):
    from app.models.operations import SalesOrder
    from app.models.foundation import InventoryBatch
    data={'location_id':farm.id,'product_id':tomatoes.id,'date':str(local_today()-timedelta(days=10)),
          'stockout':False,'source':'Farm book page 1','use_sales_ledger':False,'quantity':'13.25'}
    assert client.post('/api/v1/planning/demand-days',json=data).status_code==201
    assert db.query(SalesOrder).count()==db.query(InventoryBatch).count()==0


def test_training_without_data_is_blocked(client,db,farm,tomatoes):
    route=SupplyRoute(organization_id=farm.organization_id,name='test',origin_location_id=farm.id,dest_location_id=str(uuid4()),base_lead_time_days=1)
    db.add(route);db.commit()
    response=client.post('/api/v1/planning/train',json={'location_id':farm.id,'product_id':tomatoes.id,'route_id':route.id})
    assert response.status_code==422 and '120' in response.text
    assert db.query(ForecastRun).count()==0


def test_unauthenticated_access(unauthenticated_client,farm):
    assert unauthenticated_client.get('/api/v1/planning/runs',params={'location_id':farm.id}).status_code==401


def test_foreign_run_hidden(client,db,farm,tomatoes):
    other=Organization(id=str(uuid4()),name='Other');db.add(other);db.flush()
    run=ForecastRun(organization_id=other.id,location_id=farm.id,product_id=tomatoes.id,route_id=str(uuid4()),status='validated',result={})
    db.add(run);db.commit()
    assert client.get(f'/api/v1/planning/runs/{run.id}').status_code==404
    assert client.post(f'/api/v1/planning/runs/{run.id}/plan').status_code==404


def test_stockout_blocks_training(db,farm,tomatoes):
    today=local_today()
    for n in range(120,0,-1):
        db.add(DemandDay(organization_id=farm.organization_id,location_id=farm.id,product_id=tomatoes.id,
            date=today-timedelta(days=n),quantity=2,stockout=n==10,source='test-only'))
    db.commit()
    with pytest.raises(ValueError,match='stockout'):demand_history(db,farm.organization_id,farm.id,tomatoes.id)


def test_rejected_models_do_not_publish_forecasts(monkeypatch):
    import app.services.demand_model as module
    history,weather=series()
    monkeypatch.setattr(module,'fit_predict',lambda name,x,y,future:(np.full((len(future),3),100000.),{}))
    result=module.train_validate(history,weather)
    assert result['status']=='rejected' and 'forecasts' not in result and 'artifact' not in result


def test_confirm_ledger_uses_nairobi_day_boundaries(client,db,farm,tomatoes):
    from datetime import datetime, time, timezone
    from app.models.operations import SalesOrder, SalesOrderItem
    day=local_today()-timedelta(days=2)
    instant=datetime.combine(day-timedelta(days=1),time(22),tzinfo=timezone.utc)
    for i,hours in enumerate((0,24)):
        order=SalesOrder(organization_id=farm.organization_id,location_id=farm.id,recorded_by=1,
            client_event_id=str(uuid4()),request_hash='a'*64,sold_at=instant+timedelta(hours=hours),total_amount=10)
        db.add(order);db.flush()
        db.add(SalesOrderItem(order_id=order.id,product_id=tomatoes.id,quantity=i+2,unit='kg',unit_price=1,total_amount=i+2))
    db.commit()
    response=client.post('/api/v1/planning/demand-days',json={'location_id':farm.id,'product_id':tomatoes.id,
        'date':str(day),'stockout':False,'source':'checked ledger','use_sales_ledger':True})
    assert response.status_code==201,response.text
    assert float(response.json()['quantity'])==2


def test_fresh_weather_required_and_plan_saved(db,farm,tomatoes):
    from app.models.foundation import Location, utcnow
    from app.services.planning_service import current_plan
    destination=Location(organization_id=farm.organization_id,name='Depot',location_type='DEPOT',latitude=1,longitude=38,weather_grid_key='other')
    db.add(destination);db.flush()
    route=SupplyRoute(organization_id=farm.organization_id,name='Test route',origin_location_id=destination.id,
        dest_location_id=farm.id,base_lead_time_days=1,unpaved_ratio=.1,unknown_surface_ratio=.1,inspected_at=utcnow(),
        route_geometry={'type':'LineString','coordinates':[[38,1],[37,0]]})
    db.add(route);db.flush()
    days=[str(local_today()+timedelta(days=i)) for i in range(14)]
    run=ForecastRun(organization_id=farm.organization_id,location_id=farm.id,product_id=tomatoes.id,route_id=route.id,status='validated',
        result={'selected_model':'test-model','demand_std':2,'forecasts':[{'date':day,'p10':5,'p50':10,'p90':15} for day in days]})
    db.add(run);db.commit()
    def weather(url,params,**kwargs):return {'daily':{'time':days,'rain_sum':[10]*14,'temperature_2m_max':[28]*14}}
    plan=current_plan(db,run,fetch=weather)
    assert plan['recommended_order_quantity']>=0 and route.adjusted_lead_time_days>1
    with pytest.raises(ValueError,match='unavailable'):current_plan(db,run,fetch=lambda *a,**k:{'daily':{'time':[]}})
    run.result={**run.result,'forecasts':run.result['forecasts'][1:]}
    with pytest.raises(ValueError,match='yesterday'):current_plan(db,run,fetch=weather)
    run.result={**run.result,'forecasts':[{'date':day,'p50':10} for day in days]}
    route.dest_location_id=destination.id
    with pytest.raises(ValueError,match='incoming route'):current_plan(db,run,fetch=weather)


def test_worker_persists_blocked_run_and_does_not_reexecute(db,engine,farm,tomatoes,monkeypatch):
    from sqlalchemy.orm import sessionmaker
    from app.workers import tasks
    route=SupplyRoute(organization_id=farm.organization_id,name='test route',origin_location_id=farm.id,
        dest_location_id=str(uuid4()),base_lead_time_days=1)
    db.add(route);db.flush()
    run=ForecastRun(organization_id=farm.organization_id,location_id=farm.id,product_id=tomatoes.id,route_id=route.id,status='queued')
    db.add(run);db.commit()
    monkeypatch.setattr(tasks,'SessionLocal',sessionmaker(bind=engine))
    first=tasks.train_demand.run(farm.organization_id,run.id)
    assert first['status']=='blocked' and '120' in first['message']
    second=tasks.train_demand.run(farm.organization_id,run.id)
    assert second['status']=='blocked'
    db.refresh(run);assert run.status=='blocked'


def test_queue_failure_is_persisted(client,db,farm,tomatoes,monkeypatch):
    from fastapi import HTTPException
    from app.api.endpoints import planning
    route=SupplyRoute(organization_id=farm.organization_id,name='test route',origin_location_id=farm.id,
        dest_location_id=str(uuid4()),base_lead_time_days=1)
    db.add(route);db.commit()
    monkeypatch.setattr(planning,'demand_history',lambda *a:None)
    def unavailable(*args):raise HTTPException(503,'Queue unavailable')
    monkeypatch.setattr(planning,'queue',unavailable)
    response=client.post('/api/v1/planning/train',json={'location_id':farm.id,'product_id':tomatoes.id,'route_id':route.id})
    assert response.status_code==503
    assert db.query(ForecastRun).one().status=='queue_failed'


def test_passing_real_model_refits_and_publishes_future_horizon():
    history,weather=series()
    history=pd.Series(10+np.arange(len(history))*.5,index=history.index,name='quantity')
    # Archive is delayed: future predictions must still work without the last 7 weather days.
    result=train_validate(history,weather.iloc[:-7])
    assert result['status']=='validated',result['candidates']
    assert len(result['forecasts'])==14 and result['artifact']['format'] in ('prophet-json','lightgbm-text')
    assert result['forecasts'][0]['date']==str((history.index[-1]+pd.Timedelta(days=1)).date())
    assert result['forecasts'][-1]['date']==str((history.index[-1]+pd.Timedelta(days=14)).date())
