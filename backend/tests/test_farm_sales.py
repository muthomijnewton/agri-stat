from datetime import timedelta
from decimal import Decimal
from uuid import uuid4
import pytest
from app.models.foundation import Organization, Location, InventoryBatch, DEFAULT_ORGANIZATION_ID, utcnow
from app.models.models import Product
from app.models.operations import SalesOrder, SalesOrderItem, SaleAllocation

@pytest.fixture
def farm(db):
    db.add(Organization(id=DEFAULT_ORGANIZATION_ID,name='Test organization'))
    row=Location(name='Test farm',location_type='FARM',latitude=0,longitude=37,weather_grid_key='grid',organization_id=DEFAULT_ORGANIZATION_ID)
    db.add(row);db.commit();return row

@pytest.fixture
def tomatoes(db):
    row=Product(name='Tomatoes',unit='kg',is_active=True,shelf_life_days=7)
    db.add(row);db.commit();return row

def batch(db,farm,product,qty,expires_days=None,received_days=-1,synthetic=False):
    row=InventoryBatch(organization_id=farm.organization_id,location_id=farm.id,product_id=product.id,
        batch_code=str(uuid4()),quantity_on_hand=Decimal(qty),unit_cost=10,
        received_at=utcnow()+timedelta(days=received_days),
        expires_at=utcnow()+timedelta(days=expires_days) if expires_days is not None else None,status='ACTIVE',is_synthetic=synthetic)
    db.add(row);db.commit();return row

def payload(farm,product,qty='5',price='50.00'):
    return {'client_event_id':str(uuid4()),'location_id':farm.id,
        'items':[{'product_id':product.id,'quantity':qty,'unit_price':price}]}

def test_fefo_split_and_audit(client,db,farm,tomatoes):
    later=batch(db,farm,tomatoes,'10',expires_days=3)
    sooner=batch(db,farm,tomatoes,'3.25',expires_days=1)
    undated=batch(db,farm,tomatoes,'20')
    r=client.post('/api/v1/sales',json=payload(farm,tomatoes,'5.5'))
    assert r.status_code==201,r.text
    data=r.json()
    assert Decimal(data['total_amount'])==Decimal('275')
    assert {a['batch_id']:Decimal(a['quantity']) for a in data['items'][0]['allocations']}=={sooner.id:Decimal('3.25'),later.id:Decimal('2.25')}
    for row in (later,sooner,undated):db.refresh(row)
    assert sooner.quantity_on_hand==0 and sooner.status=='DEPLETED'
    assert later.quantity_on_hand==Decimal('7.75') and undated.quantity_on_hand==20

def test_retries_are_exactly_once_and_changed_event_is_rejected(client,db,farm,tomatoes):
    row=batch(db,farm,tomatoes,'10',expires_days=2);body=payload(farm,tomatoes)
    first=client.post('/api/v1/sales',json=body)
    body['items'][0]['quantity']='5.0000'
    second=client.post('/api/v1/sales',json=body)
    assert first.status_code==201 and second.status_code==200
    assert first.json()['id']==second.json()['id'] and second.json()['replayed']
    body['items'][0]['unit_price']='51'
    assert client.post('/api/v1/sales',json=body).status_code==409
    db.refresh(row);assert row.quantity_on_hand==5
    assert db.query(SalesOrder).count()==db.query(SaleAllocation).count()==1

@pytest.mark.parametrize('kwargs',[{'expires_days':-1},{'received_days':1},{'synthetic':True}])
def test_unusable_stock_excluded(client,db,farm,tomatoes,kwargs):
    row=batch(db,farm,tomatoes,'10',**kwargs)
    assert client.post('/api/v1/sales',json=payload(farm,tomatoes)).status_code==409
    db.refresh(row);assert row.quantity_on_hand==10
    assert db.query(SalesOrder).count()==0

def test_insufficient_cart_is_atomic(client,db,farm,tomatoes):
    row=batch(db,farm,tomatoes,'10')
    other=Product(name='Potatoes',unit='kg',is_active=True);db.add(other);db.commit()
    body=payload(farm,tomatoes);body['items'].append({'product_id':other.id,'quantity':'1','unit_price':'25'})
    assert client.post('/api/v1/sales',json=body).status_code==409
    db.refresh(row);assert row.quantity_on_hand==10
    assert db.query(SalesOrder).count()==db.query(SalesOrderItem).count()==db.query(SaleAllocation).count()==0

def test_organization_boundaries(client,db,farm,tomatoes):
    other=Organization(id=str(uuid4()),name='Other');db.add(other);db.commit()
    foreign=Location(name='Other',location_type='FARM',latitude=1,longitude=37,weather_grid_key='other',organization_id=other.id)
    db.add(foreign);db.commit()
    assert client.post('/api/v1/sales',json=payload(foreign,tomatoes)).status_code==404
    assert client.get('/api/v1/stock',params={'location_id':foreign.id}).status_code==404
    tomatoes.organization_id=other.id;db.commit()
    assert client.post('/api/v1/sales',json=payload(farm,tomatoes)).status_code==404

def test_stock_summary(client,db,farm,tomatoes):
    batch(db,farm,tomatoes,'4',expires_days=-1);batch(db,farm,tomatoes,'3',expires_days=1)
    batch(db,farm,tomatoes,'2');batch(db,farm,tomatoes,'9',received_days=1);batch(db,farm,tomatoes,'20',synthetic=True)
    r=client.get('/api/v1/stock',params={'location_id':farm.id});assert r.status_code==200
    row=r.json()['items'][0]
    assert Decimal(row['available'])==5 and Decimal(row['expired'])==4 and Decimal(row['unknown_expiry'])==2

@pytest.mark.parametrize('qty,price',[('0','1'),('-1','1'),('1','-1'),('1.00001','1'),('NaN','1'),('1','Infinity')])
def test_invalid_numbers(client,farm,tomatoes,qty,price):
    assert client.post('/api/v1/sales',json=payload(farm,tomatoes,qty,price)).status_code==422

def test_duplicate_product(client,farm,tomatoes):
    body=payload(farm,tomatoes);body['items']*=2
    assert client.post('/api/v1/sales',json=body).status_code==422

def test_readiness_requires_real_sales(client,farm):
    row=client.get('/api/v1/forecast-readiness',params={'location_id':farm.id}).json()
    assert row['sales_recorded']==0 and row['demand_model_ready'] is False

def test_authentication_required(unauthenticated_client,farm,tomatoes):
    assert unauthenticated_client.post('/api/v1/sales',json=payload(farm,tomatoes)).status_code==401

def test_receipt_timestamps_normalized_to_utc():
    from app.schemas.foundation import BatchCreate
    data=BatchCreate(location_id=uuid4(),product_id=1,batch_code='lot',quantity_on_hand='2',unit_cost='1',
        received_at='2026-11-13T10:00:00+03:00',expires_at='2026-11-14T10:00:00+03:00')
    assert data.received_at.hour==7 and data.received_at.utcoffset()==timedelta(0)
    assert data.expires_at.hour==7 and data.expires_at.utcoffset()==timedelta(0)
