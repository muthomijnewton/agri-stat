// GENERATED CODE - manually added

part of 'recommendation_model.dart';

InventoryRecommendation _$InventoryRecommendationFromJson(Map<String, dynamic> json) => InventoryRecommendation(
      id: json['id'] as int,
      productId: (json['product_id'] ?? json['productId']) as int,
      recommendedQuantity: (json['recommended_quantity'] ?? json['recommendedQuantity']) as int,
      currentQuantity: (json['current_quantity'] ?? json['currentQuantity']) as int?,
      minQuantity: (json['min_quantity'] ?? json['minQuantity']) as int?,
      maxQuantity: (json['max_quantity'] ?? json['maxQuantity']) as int?,
      recommendationDate: DateTime.parse(json['recommendation_date'] ?? json['recommendationDate']),
      reason: (json['reason'] ?? json['reason']) as String?,
      status: (json['status'] ?? json['status']) as String,
      createdAt: DateTime.parse(json['created_at'] ?? json['createdAt']),
      updatedAt: (json['updated_at'] ?? json['updatedAt']) == null
          ? null
          : DateTime.parse(json['updated_at'] ?? json['updatedAt']),
    );

Map<String, dynamic> _$InventoryRecommendationToJson(InventoryRecommendation instance) => <String, dynamic>{
      'id': instance.id,
      'product_id': instance.productId,
      'recommended_quantity': instance.recommendedQuantity,
      'current_quantity': instance.currentQuantity,
      'min_quantity': instance.minQuantity,
      'max_quantity': instance.maxQuantity,
      'recommendation_date': instance.recommendationDate.toIso8601String(),
      'reason': instance.reason,
      'status': instance.status,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };
