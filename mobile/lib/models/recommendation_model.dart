import 'package:json_annotation/json_annotation.dart';

part 'recommendation.g.dart';

@JsonSerializable()
class InventoryRecommendation {
  final int id;
  final int productId;
  final int recommendedQuantity;
  final int? currentQuantity;
  final int? minQuantity;
  final int? maxQuantity;
  final DateTime recommendationDate;
  final String? reason;
  final String status;
  final DateTime createdAt;
  final DateTime? updatedAt;

  InventoryRecommendation({
    required this.id,
    required this.productId,
    required this.recommendedQuantity,
    this.currentQuantity,
    this.minQuantity,
    this.maxQuantity,
    required this.recommendationDate,
    this.reason,
    required this.status,
    required this.createdAt,
    this.updatedAt,
  });

  factory InventoryRecommendation.fromJson(Map<String, dynamic> json) => _$InventoryRecommendationFromJson(json);
  Map<String, dynamic> toJson() => _$InventoryRecommendationToJson(this);
}
