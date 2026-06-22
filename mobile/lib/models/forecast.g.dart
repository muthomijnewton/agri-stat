// GENERATED CODE - manually added to satisfy analyzer for build_runner absence

part of 'forecast_model.dart';

Forecast _$ForecastFromJson(Map<String, dynamic> json) => Forecast(
      id: json['id'] as int,
      productId: (json['product_id'] ?? json['productId']) as int,
      forecastDate: DateTime.parse(json['forecast_date'] ?? json['forecastDate']),
      predictedDemand: (json['predicted_demand'] ?? json['predictedDemand']) as int,
      confidenceLower: (json['confidence_lower'] ?? json['confidenceLower']) != null
          ? (json['confidence_lower'] ?? json['confidenceLower']).toDouble()
          : null,
      confidenceUpper: (json['confidence_upper'] ?? json['confidenceUpper']) != null
          ? (json['confidence_upper'] ?? json['confidenceUpper']).toDouble()
          : null,
      modelType: (json['model_type'] ?? json['modelType']) as String?,
      accuracyScore: (json['accuracy_score'] ?? json['accuracyScore']) != null
          ? (json['accuracy_score'] ?? json['accuracyScore']).toDouble()
          : null,
      createdAt: DateTime.parse(json['created_at'] ?? json['createdAt']),
      updatedAt: (json['updated_at'] ?? json['updatedAt']) == null
          ? null
          : DateTime.parse(json['updated_at'] ?? json['updatedAt']),
    );

Map<String, dynamic> _$ForecastToJson(Forecast instance) => <String, dynamic>{
      'id': instance.id,
      'product_id': instance.productId,
      'forecast_date': instance.forecastDate.toIso8601String(),
      'predicted_demand': instance.predictedDemand,
      'confidence_lower': instance.confidenceLower,
      'confidence_upper': instance.confidenceUpper,
      'model_type': instance.modelType,
      'accuracy_score': instance.accuracyScore,
      'created_at': instance.createdAt.toIso8601String(),
      'updated_at': instance.updatedAt?.toIso8601String(),
    };
