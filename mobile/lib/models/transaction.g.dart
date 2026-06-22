// GENERATED CODE - manually added

part of 'transaction_model.dart';

Transaction _$TransactionFromJson(Map<String, dynamic> json) => Transaction(
      id: json['id'] as int,
      productId: (json['product_id'] ?? json['productId']) as int,
      userId: (json['user_id'] ?? json['userId']) as int?,
      quantity: (json['quantity'] ?? json['quantity']) as int,
      unitPrice: (json['unit_price'] ?? json['unitPrice']) is int
          ? (json['unit_price'] ?? json['unitPrice']).toDouble()
          : (json['unit_price'] ?? json['unitPrice']) as double,
      totalPrice: (json['total_price'] ?? json['totalPrice']) is int
          ? (json['total_price'] ?? json['totalPrice']).toDouble()
          : (json['total_price'] ?? json['totalPrice']) as double,
      transactionDate: DateTime.parse(json['transaction_date'] ?? json['transactionDate']),
      notes: (json['notes'] ?? json['notes']) as String?,
      createdAt: DateTime.parse(json['created_at'] ?? json['createdAt']),
      updatedAt: (json['updated_at'] ?? json['updatedAt']) == null
          ? null
          : DateTime.parse(json['updated_at'] ?? json['updatedAt']),
    );

Map<String, dynamic> _$TransactionToJson(Transaction instance) => <String, dynamic>{
      'id': instance.id,
      'product_id': instance.productId,
      'user_id': instance.userId,
      'quantity': instance.quantity,
      'unit_price': instance.unitPrice,
      'total_price': instance.totalPrice,
      'transaction_date': instance.transactionDate.toIso8601String(),
      'notes': instance.notes,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };
