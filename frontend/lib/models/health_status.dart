class HealthStatus {
  const HealthStatus({
    required this.source,
    required this.label,
    required this.isResponding,
    required this.lastSuccessfulSync,
    required this.recordsCount,
    required this.lastError,
    required this.lastErrorAt,
  });

  final String source;
  final String label;
  final bool isResponding;
  final DateTime? lastSuccessfulSync;
  final int recordsCount;
  final String? lastError;
  final DateTime? lastErrorAt;

  factory HealthStatus.fromJson(Map<String, dynamic> json) {
    return HealthStatus(
      source: json['source'] as String,
      label: json['label'] as String,
      isResponding: json['is_responding'] as bool,
      lastSuccessfulSync: json['last_successful_sync'] != null
          ? DateTime.parse(json['last_successful_sync'] as String)
          : null,
      recordsCount: json['records_count'] as int,
      lastError: json['last_error'] as String?,
      lastErrorAt: json['last_error_at'] != null
          ? DateTime.parse(json['last_error_at'] as String)
          : null,
    );
  }
}
