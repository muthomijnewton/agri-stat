import 'package:flutter/material.dart';

class StatCard extends StatelessWidget {
  final String title;

  final String value;

  final IconData icon;

  final Color backgroundColor;

  const StatCard({
    super.key,

    required this.title,

    required this.value,

    required this.icon,

    this.backgroundColor =
        const Color(0xFF2E7D32),
  });

  @override
  Widget build(
    BuildContext context,
  ) {
    final isDark =
        Theme.of(context)
                .brightness ==
            Brightness.dark;

    return AnimatedContainer(
      duration:
          const Duration(
        milliseconds: 250,
      ),

      padding:
          const EdgeInsets.all(
        18,
      ),

      decoration: BoxDecoration(
        color: isDark
            ? const Color(
                0xFF1E1E1E,
              )
            : Colors.white,

        borderRadius:
            BorderRadius.circular(
          18,
        ),

        boxShadow: [
          BoxShadow(
            color: Colors.black
                .withValues(
              alpha: 0.06,
            ),

            blurRadius: 14,

            offset:
                const Offset(0, 6),
          ),
        ],
      ),

      child: Column(
        crossAxisAlignment:
            CrossAxisAlignment.start,

        children: [
          // ICON

          Container(
            width: 50,

            height: 50,

            decoration:
                BoxDecoration(
              color: backgroundColor
                  .withValues(
                alpha: 0.15,
              ),

              borderRadius:
                  BorderRadius.circular(
                14,
              ),
            ),

            child: Icon(
              icon,

              size: 28,

              color:
                  backgroundColor,
            ),
          ),

          const Spacer(),

          // VALUE

          Text(
            value,

            maxLines: 1,

            overflow:
                TextOverflow
                    .ellipsis,

            style:
                const TextStyle(
              fontSize: 28,

              fontWeight:
                  FontWeight.bold,
            ),
          ),

          const SizedBox(
            height: 6,
          ),

          // TITLE

          Text(
            title,

            style: TextStyle(
              fontSize: 14,

              fontWeight:
                  FontWeight.w500,

              color: isDark

                  ? Colors.grey[400]

                  : Colors.grey[700],
            ),
          ),
        ],
      ),
    );
  }
}