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

  String _formatPrice(double? price) {
    if (price == null) return '--';

    return price.toStringAsFixed(0);
  }

  @override
  Widget build(BuildContext context) {
    final color = _categoryColor(widget.category);

    final isDark =
        Theme.of(context).brightness ==
            Brightness.dark;

    return Hero(
      tag: 'product_${widget.id}',

      child: GestureDetector(
        onTapDown: (_) {
          setState(() {
            _pressed = true;
          });
        },

        onTapUp: (_) {
          setState(() {
            _pressed = false;
          });
        },

        onTapCancel: () {
          setState(() {
            _pressed = false;
          });
        },

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
          duration: const Duration(
            milliseconds: 150,
          ),

          curve: Curves.easeOut,

          transform: Matrix4.identity()
  ..scale(
    _pressed ? 0.98 : 1.0,
  ),

          margin:
              const EdgeInsets.symmetric(
            vertical: 8,
          ),

          padding:
              const EdgeInsets.all(14),

          decoration: BoxDecoration(
            borderRadius:
                BorderRadius.circular(18),

            color: isDark
                ? const Color(
                    0xFF1E1E1E,
                  )
                : Colors.white,

            boxShadow: [
              BoxShadow(
                color: Colors.black
                    .withValues(
                  alpha: 0.06,
                ),

                blurRadius: 12,

                offset: const Offset(
                  0,
                  6,
                ),
              ),
            ],
          ),

          child: Row(
            children: [
              // ======================
              // ICON
              // ======================

              Container(
                width: 56,

                height: 56,

                decoration: BoxDecoration(
                  color: color.withValues(
                    alpha: 0.12,
                  ),

                  borderRadius:
                      BorderRadius.circular(
                    14,
                  ),
                ),

                child: Icon(
                  Icons.agriculture,

                  size: 28,

                  color: color,
                ),
              ),

              const SizedBox(
                width: 14,
              ),

              // ======================
              // TEXT
              // ======================

              Expanded(
                child: Column(
                  crossAxisAlignment:
                      CrossAxisAlignment
                          .start,

                  children: [
                    Text(
                      widget.name,

                      maxLines: 1,

                      overflow:
                          TextOverflow
                              .ellipsis,

                      style:
                          const TextStyle(
                        fontSize: 17,

                        fontWeight:
                            FontWeight.bold,
                      ),
                    ),

                    const SizedBox(
                      height: 5,
                    ),

                    Container(
                      padding:
                          const EdgeInsets.symmetric(
                        horizontal: 10,

                        vertical: 4,
                      ),

                      decoration:
                          BoxDecoration(
                        color: color
                            .withValues(
                          alpha: 0.12,
                        ),

                        borderRadius:
                            BorderRadius.circular(
                          20,
                        ),
                      ),

                      child: Text(
                        widget.category ??
                            'Uncategorized',

                        style:
                            TextStyle(
                          color: color,

                          fontWeight:
                              FontWeight.w600,

                          fontSize: 12,
                        ),
                      ),
                    ),

                    const SizedBox(
                      height: 8,
                    ),

                    if (widget.unit != null &&
                        widget.unit!.isNotEmpty)
                      Text(
                        widget.unit!,

                        style:
                            TextStyle(
                          color:
                              Colors.grey[
                                  500],

                          fontSize: 12,
                        ),
                      ),
                  ],
                ),
              ),

              // ======================
              // PRICE
              // ======================

              Column(
                mainAxisAlignment:
                    MainAxisAlignment
                        .center,

                crossAxisAlignment:
                    CrossAxisAlignment
                        .end,

                children: [
                  Text(
                    'KES ${_formatPrice(widget.price)}',

                    style: TextStyle(
                      color: color,

                      fontWeight:
                          FontWeight.bold,

                      fontSize: 16,
                    ),
                  ),

                  const SizedBox(
                    height: 10,
                  ),

                  Icon(
                    Icons.arrow_forward_ios,

                    size: 14,

                    color:
                        Colors.grey[400],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}