import 'package:flutter/material.dart';
import '../screens/product_details_screen.dart';

class ProductCard extends StatelessWidget {
  final int id;
  final String name;
  final String? category;
  final double? price;
  final String? unit;

  const ProductCard({
    super.key,
    required this.id,
    required this.name,
    this.category,
    this.price,
    this.unit,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: ListTile(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => ProductDetailsScreen(
                productId: id,
                productName: name,
              ),
            ),
          );
        },

        leading: Container(
          width: 50,
          height: 50,
          decoration: BoxDecoration(
            color: const Color(0xFF2E7D32).withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(
            Icons.agriculture,
            color: Color(0xFF2E7D32),
          ),
        ),

        title: Text(
          name,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),

        subtitle: Text(
          category ?? 'Uncategorized',
          style: TextStyle(color: Colors.grey[600]),
        ),

        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            if (price != null)
              Text(
                'KES ${price!.toStringAsFixed(0)}',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF2E7D32),
                ),
              ),
            if (unit != null)
              Text(
                unit!,
                style: const TextStyle(
                  fontSize: 12,
                  color: Colors.grey,
                ),
              ),
          ],
        ),
      ),
    );
  }
}