import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/health_status.dart';

/// Cliente HTTP mínimo para o backend do painel.
///
/// `baseUrl` é definido em tempo de build via `--dart-define=API_BASE_URL=...`
/// (ver frontend/Dockerfile), com `http://localhost:8000` como padrão para
/// rodar localmente com `flutter run -d chrome`.
class ApiClient {
  ApiClient({String? baseUrl})
      : baseUrl = baseUrl ??
            const String.fromEnvironment(
              'API_BASE_URL',
              defaultValue: 'http://localhost:8000',
            );

  final String baseUrl;

  Future<List<HealthStatus>> fetchHealth() async {
    final uri = Uri.parse('$baseUrl/health');
    final response = await http.get(uri).timeout(const Duration(seconds: 10));

    if (response.statusCode != 200) {
      throw Exception(
        'Falha ao consultar /health (HTTP ${response.statusCode})',
      );
    }

    final data = jsonDecode(response.body) as List<dynamic>;
    return data
        .map((item) => HealthStatus.fromJson(item as Map<String, dynamic>))
        .toList();
  }
}
