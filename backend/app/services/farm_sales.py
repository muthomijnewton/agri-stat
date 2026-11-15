"""Atomic FEFO stock consumption. Public price observations never become sales."""
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from sqlalchemy import case, or_, update
from app.models.foundation import InventoryBatch, Location, Organization, utcnow
from app.models.models import Product
from app.models.operations import SalesOrder, SalesOrderItem, SaleAllocation
from app.services.inventory_service import batch_status


class SaleError(Exception):
    def __init__(self, message, status=409):
        self.status = status
        super().__init__(message)


def fingerprint(request):
    payload = {'location_id': str(request.location_id), 'items': [
        {'product_id': item.product_id, 'quantity': format(item.quantity.normalize(), 'f'),
         'unit_price': format(item.unit_price.normalize(), 'f')}
        for item in sorted(request.items, key=lambda item: item.product_id)]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def replay(db, organization_id, request):
    existing = db.query(SalesOrder).filter_by(organization_id=organization_id,
        client_event_id=str(request.client_event_id)).first()
    if existing and existing.request_hash != fingerprint(request):
        raise SaleError('This event ID was already used for a different sale')
    return existing


def record_sale(db, user, request, *, now=None):
    now = now or utcnow()
    # A short organization lock serializes checkout and retries on PostgreSQL.
    # Batch updates also check remaining quantity, including on SQLite.
    organization = db.query(Organization).filter_by(id=user.organization_id).with_for_update().first()
    if not organization:
        raise SaleError('Organization not found', 404)
    existing = replay(db, user.organization_id, request)
    if existing:
        return existing, True
    location = db.query(Location).filter_by(id=str(request.location_id), organization_id=user.organization_id).first()
    if not location:
        raise SaleError('Location not found', 404)
    plans = []
    for item in sorted(request.items, key=lambda row: row.product_id):
        product = db.query(Product).filter_by(id=item.product_id, organization_id=user.organization_id, is_active=True).first()
        if not product:
            raise SaleError('Active product not found', 404)
        if not product.unit:
            raise SaleError('Set the product unit before recording a sale', 422)
        batches = db.query(InventoryBatch).filter(
            InventoryBatch.organization_id == user.organization_id,
            InventoryBatch.location_id == location.id,
            InventoryBatch.product_id == product.id,
            InventoryBatch.is_synthetic.is_(False),
            InventoryBatch.quantity_on_hand > 0,
            InventoryBatch.received_at <= now,
            or_(InventoryBatch.expires_at.is_(None), InventoryBatch.expires_at > now),
        ).order_by(case((InventoryBatch.expires_at.is_(None), 1), else_=0),
                   InventoryBatch.expires_at, InventoryBatch.received_at, InventoryBatch.id).with_for_update().all()
        available = sum((b.quantity_on_hand for b in batches), Decimal(0))
        if available < item.quantity:
            raise SaleError(f'Insufficient usable stock for {product.name}: requested {item.quantity} {product.unit}; available {available} {product.unit}')
        plans.append((item, product, batches))
    total = sum(((item.quantity * item.unit_price).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
                 for item, _, _ in plans), Decimal(0))
    if total > Decimal('9999999999999999.99'):
        raise SaleError('Sale total exceeds the supported amount', 422)
    order = SalesOrder(organization_id=user.organization_id, location_id=location.id,
        recorded_by=user.id, client_event_id=str(request.client_event_id), request_hash=fingerprint(request),
        sold_at=now, total_amount=Decimal(0), currency='KES')
    db.add(order)
    db.flush()
    for item, product, batches in plans:
        line_total = (item.quantity * item.unit_price).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        line = SalesOrderItem(order_id=order.id, product_id=product.id, unit=product.unit,
            quantity=item.quantity, unit_price=item.unit_price, total_amount=line_total)
        db.add(line)
        db.flush()
        remaining = item.quantity
        for batch in batches:
            if remaining <= 0:
                break
            take = min(remaining, batch.quantity_on_hand)
            changed = db.execute(update(InventoryBatch).where(InventoryBatch.id == batch.id,
                InventoryBatch.quantity_on_hand >= take).values(
                    quantity_on_hand=InventoryBatch.quantity_on_hand - take, updated_at=now),
                    execution_options={'synchronize_session': False})
            if changed.rowcount != 1:
                raise SaleError('Stock changed during checkout. Retry with the same event ID')
            db.refresh(batch)
            batch.status = batch_status(batch, now)
            db.add(SaleAllocation(order_item_id=line.id, batch_id=batch.id, quantity=take))
            remaining -= take
        order.total_amount += line_total
    db.flush()
    return order, False


def sale_result(db, order, *, replayed=False):
    lines = db.query(SalesOrderItem).filter_by(order_id=order.id).order_by(SalesOrderItem.product_id).all()
    return {'id': order.id, 'client_event_id': order.client_event_id, 'location_id': order.location_id,
        'sold_at': order.sold_at, 'currency': order.currency, 'total_amount': str(order.total_amount),
        'replayed': replayed, 'items': [dict(product_id=line.product_id, quantity=str(line.quantity),
            unit=line.unit, unit_price=str(line.unit_price), total_amount=str(line.total_amount),
            allocations=[{'batch_id': a.batch_id, 'batch_code': db.get(InventoryBatch, a.batch_id).batch_code, 'quantity': str(a.quantity)} for a in db.query(SaleAllocation)
                .filter_by(order_item_id=line.id).order_by(SaleAllocation.id).all()]) for line in lines]}
