"""Real PostgreSQL concurrency checks for stock and duplicate sale submissions."""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import os
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.db.database import Base
from app.models.foundation import Organization, Location, InventoryBatch, utcnow
from app.models.models import Product, User
from app.models.operations import SalesOrder
from app.schemas.operations import SaleCreate
from app.services.farm_sales import record_sale, SaleError

pytestmark = pytest.mark.skipif(not os.getenv('PHASE1_POSTGRES_TEST_URL'), reason='PostgreSQL integration URL not configured')

@pytest.mark.parametrize('same_event', [False, True])
def test_concurrent_sales_cannot_oversell_or_double_apply(same_event):
    raw = create_engine(os.environ['PHASE1_POSTGRES_TEST_URL'])
    schema = 'sales_test_' + uuid4().hex
    with raw.begin() as connection: connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = raw.execution_options(schema_translate_map={None:schema})
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            org=Organization(id=str(uuid4()),name='Concurrency test');db.add(org);db.flush()
            user=User(username='test',email='test@example.com',password='unused',organization_id=org.id)
            farm=Location(name='Test',location_type='FARM',latitude=0,longitude=37,weather_grid_key='test',organization_id=org.id)
            product=Product(name='Produce',unit='kg',is_active=True,organization_id=org.id)
            db.add_all([user,farm,product]);db.flush()
            batch=InventoryBatch(organization_id=org.id,location_id=farm.id,product_id=product.id,batch_code='lot',quantity_on_hand=10,unit_cost=1,received_at=utcnow(),status='ACTIVE',is_synthetic=False)
            db.add(batch);db.commit()
            who=SimpleNamespace(id=user.id,organization_id=org.id)
            loc, prod, batch_id = farm.id,product.id,batch.id
        barrier=Barrier(2)
        event=str(uuid4())
        def sell(index):
            request=SaleCreate(client_event_id=event if same_event else str(uuid4()),location_id=loc,items=[{'product_id':prod,'quantity':'7','unit_price':'20'}])
            with Session(engine) as db:
                barrier.wait(timeout=5)
                try:
                    order,replayed=record_sale(db,who,request);db.commit()
                    return ('ok',order.id,replayed)
                except SaleError:
                    db.rollback();return ('shortage',None,False)
        with ThreadPoolExecutor(max_workers=2) as executor:
            results=list(executor.map(sell,[0,1]))
        with Session(engine) as db:
            assert db.get(InventoryBatch,batch_id).quantity_on_hand==Decimal('3')
            assert db.query(SalesOrder).count()==1
        if same_event:
            assert all(r[0]=='ok' for r in results)
            assert results[0][1]==results[1][1]
            assert sorted(r[2] for r in results)==[False,True]
        else:
            assert sorted(r[0] for r in results)==['ok','shortage']
    finally:
        with raw.begin() as connection: connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        raw.dispose()
