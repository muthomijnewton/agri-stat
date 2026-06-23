import 'package:flutter/material.dart';
import '../screens/product_details_screen.dart';

class ProductCard extends StatefulWidget {
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
  State<ProductCard> createState() => _ProductCardState();
}

class _ProductCardState extends State<ProductCard>
    with SingleTickerProviderStateMixin {
  bool _pressed = false;

  Color _categoryColor(String? category) {
    switch ((category ?? '').toLowerCase()) {
      case 'vegetables':
        return Colors.green;
      case 'fruits':
        return Colors.orange;
      case 'grains':
        return Colors.brown;
      case 'dairy':
        return Colors.blue;
      default:
        return const Color(0xFF2E7D32);
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _categoryColor(widget.category);

    return GestureDetector(
      onTapDown: (_) => setState(() => _pressed = true),
      onTapUp: (_) => setState(() => _pressed = false),
      onTapCancel: () => setState(() => _pressed = false),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => ProductDetailsScreen(
              productId: widget.id,
              productName: widget.name,
            ),
          ),
        );
      },
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        transform: Matrix4.identity()
          ..scale(_pressed ? 0.98 : 1.0),

        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.all(14),

        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          color: Colors.white,
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.05),
              blurRadius: 12,
              offset: const Offset(0, 6),
            ),
          ],
        ),

        child: Row(
          children: [
            // ICON SECTION
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                Icons.agriculture,
                color: color,
              ),
            ),

            const SizedBox(width: 12),

            // TEXT SECTION
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.name,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),

                  const SizedBox(height: 4),

                  Text(
                    widget.category ?? 'Uncategorized',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),

                  const SizedBox(height: 6),

                  if (widget.unit != null)
                    Text(
                      widget.unit!,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[500],
                      ),
                    ),
                ],
              ),
            ),

            // PRICE SECTION
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                if (widget.price != null)
                  Text(
                    'KES ${widget.price!.toStringAsFixed(0)}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                      color: color,
                    ),
                  ),

                const SizedBox(height: 6),

                Icon(
                  Icons.arrow_forward_ios,
                  size: 14,
                  color: Colors.grey[400],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}