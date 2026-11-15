"""Phase 3 projections and historical import never synthesize inventory."""
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4
import pytest
from app.models.foundation import Organization, Location, WeatherObservation, InventoryBatch, utcnow
from app.models.models import Product
from app.models.planning import DemandDay
from app.models.operations import SalesOrder
from app.services.planning_service import local_today
from tests.test_farm_sales import farm, tomatoes, batch


def upload(client,farm,product,text,**options):
    return client.post('/api/v1/admin/import-csv',data={'location_id':farm.id,'product_id':product.id,**options},
        files={'file':('history.csv',text.encode(),'text/csv')})


def csv_text(days=None):
    days=days or [local_today()-timedelta(days=2),local_today()-timedelta(days=1)]
    return 'date,quantity,stockout,source\n'+''.join(f'{d},12.5,false,Farm sales book\n' for d in days)


def test_preview_then_atomic_import(client,db,farm,tomatoes):
    content=csv_text();preview=upload(client,farm,tomatoes,content)
    assert preview.status_code==200,preview.text
    result=preview.json();assert result['status']=='preview' and result['row_count']==2
    assert db.query(DemandDay).count()==0
    commit=upload(client,farm,tomatoes,content,commit='true',preview_hash=result['preview_hash'])
    assert commit.json()['imported_rows']==2
    assert db.query(DemandDay).count()==2
    assert db.query(InventoryBatch).count()==db.query(SalesOrder).count()==0
    retry=upload(client,farm,tomatoes,content)
    assert retry.json()['status']=='invalid' and retry.json()['error_count']==2
    assert db.query(DemandDay).count()==2


def test_invalid_row_prevents_every_insert(client,db,farm,tomatoes):
    content=csv_text()+f'{local_today()},-3,maybe,invalid\n'
    response=upload(client,farm,tomatoes,content)
    assert response.json()['status']=='invalid' and response.json()['valid_rows']==2
    assert db.query(DemandDay).count()==0


def test_changed_file_and_wrong_product_cannot_reuse_preview(client,db,farm,tomatoes):
    content=csv_text();digest=upload(client,farm,tomatoes,content).json()['preview_hash']
    assert upload(client,farm,tomatoes,content.replace('12.5','13'),commit='true',preview_hash=digest).status_code==409
    other=Product(name='Other crop',unit='kg');db.add(other);db.commit()
    assert upload(client,farm,other,content,commit='true',preview_hash=digest).status_code==409
    assert db.query(DemandDay).count()==0


@pytest.mark.parametrize('content',[
    'date,price,market\n2020-01-01,20,Nairobi\n',
    'date,quantity,stockout,source,source\n',
    'date,quantity,stockout,source\n',
])
def test_wrong_csv_schema_rejected(client,farm,tomatoes,content):
    assert upload(client,farm,tomatoes,content).status_code==422


def test_duplicate_dates_are_reported(client,db,farm,tomatoes):
    day=local_today()-timedelta(days=2)
    response=upload(client,farm,tomatoes,csv_text([day,day]))
    assert response.json()['status']=='invalid'
    assert db.query(DemandDay).count()==0


def test_preview_commit_race_rolls_back(client,db,farm,tomatoes):
    content=csv_text();digest=upload(client,farm,tomatoes,content).json()['preview_hash']
    db.add(DemandDay(organization_id=farm.organization_id,location_id=farm.id,product_id=tomatoes.id,
        date=local_today()-timedelta(days=1),quantity=1,stockout=False,source='existing'));db.commit()
    response=upload(client,farm,tomatoes,content,commit='true',preview_hash=digest)
    assert response.json()['status']=='invalid' and db.query(DemandDay).count()==1


def test_dashboard_filters_unusable_stock_and_preserves_units(client,db,farm,tomatoes):
    batch(db,farm,tomatoes,'4',expires_days=1);batch(db,farm,tomatoes,'2',expires_days=-1)
    batch(db,farm,tomatoes,'9',synthetic=True);batch(db,farm,tomatoes,'7',received_days=1)
    eggs=Product(name='Eggs',unit='units',is_active=True);db.add(eggs);db.commit();batch(db,farm,eggs,'12')
    result=client.get('/api/v1/dashboard',params={'location_id':farm.id}).json()
    assert Decimal(result['available_by_unit']['kg'])==4
    assert Decimal(result['available_by_unit']['units'])==12
    assert result['batch_counts']=={'expired':1,'expiring_soon':1,'unknown_expiry':1}
    assert result['sales_count']==0 and result['batch_total']==4


def test_dashboard_and_import_tenant_boundaries(client,db,farm,tomatoes):
    other=Organization(id=str(uuid4()),name='Other tenant');db.add(other);db.commit()
    foreign=Location(organization_id=other.id,name='Foreign farm',location_type='FARM',latitude=1,longitude=37,weather_grid_key='private')
    db.add(foreign);db.commit()
    assert client.get('/api/v1/dashboard',params={'location_id':foreign.id}).status_code==404
    assert upload(client,foreign,tomatoes,csv_text()).status_code==404
    assert foreign.id not in str(client.get('/api/v1/map-data').json())


def test_partial_weather_not_reported_as_zero(client,db,farm):
    db.add(WeatherObservation(organization_id=farm.organization_id,weather_grid_key=farm.weather_grid_key,
        date=local_today(),is_forecast=True,rainfall_mm=0,soil_moisture_0_to_7cm=.2,source='test-only'))
    db.commit()
    row=client.get('/api/v1/map-data').json()['locations'][0]
    assert row['rain_3d_mm'] is None and row['soil_moisture']==.2


def test_import_requires_administrator(client,db,auth_user,farm,tomatoes):
    from app.main import app
    from app.core.security import get_current_admin
    app.dependency_overrides.pop(get_current_admin,None)
    assert upload(client,farm,tomatoes,csv_text()).status_code==403


def test_dashboard_requires_login(unauthenticated_client):
    assert unauthenticated_client.get('/api/v1/dashboard').status_code==401


def test_stale_weather_is_unknown(client,db,farm):
    for offset in range(3):
        db.add(WeatherObservation(organization_id=farm.organization_id,
            weather_grid_key=farm.weather_grid_key,date=local_today()+timedelta(days=offset),
            is_forecast=True,rainfall_mm=20,soil_moisture_0_to_7cm=.2,
            fetched_at=utcnow()-timedelta(hours=48),source='test-only'))
    db.commit()
    row=client.get('/api/v1/map-data').json()['locations'][0]
    assert row['rain_3d_mm'] is None and row['soil_moisture'] is None
