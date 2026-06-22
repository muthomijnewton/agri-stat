// GENERATED CODE - manually added

part of 'product_model.dart';

Product _$ProductFromJson(Map<String, dynamic> json) => Product(
      id: json['id'] as int,
      name: json['name'] as String,
      category: (json['category'] ?? json['category']) as String?,
      description: (json['description'] ?? json['description']) as String?,
      unitPrice: (json['unit_price'] ?? json['unitPrice']) != null
          ? (json['unit_price'] ?? json['unitPrice']).toDouble()
          : null,
      unit: (json['unit'] ?? json['unit']) as String?,
      isActive: (json['is_active'] ?? json['isActive']) as bool,
      createdAt: DateTime.parse(json['created_at'] ?? json['createdAt']),
      updatedAt: (json['updated_at'] ?? json['updatedAt']) == null
          ? null
          : DateTime.parse(json['updated_at'] ?? json['updatedAt']),
    );

Map<String, dynamic> _$ProductToJson(Product instance) => <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'category': instance.category,
      'description': instance.description,
      'unit_price': instance.unitPrice,
      'unit': instance.unit,
      'is_active': instance.isActive,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };
