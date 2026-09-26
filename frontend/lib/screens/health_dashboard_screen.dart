import 'package:flutter/material.dart';

import '../models/health_status.dart';
import '../services/api_client.dart';

/// Única tela do projeto: somente leitura, mostra o estado de cada
/// integração (respondendo agora, última sync bem-sucedida, quantidade de
/// registros e último erro).
class HealthDashboardScreen extends StatefulWidget {
  const HealthDashboardScreen({super.key, required this.apiClient});

  final ApiClient apiClient;

  @override
  State<HealthDashboardScreen> createState() => _HealthDashboardScreenState();
}

class _HealthDashboardScreenState extends State<HealthDashboardScreen> {
  late Future<List<HealthStatus>> _future;

  @override
  void initState() {
    super.initState();
    _future = widget.apiClient.fetchHealth();
  }

  void _reload() {
    setState(() {
      _future = widget.apiClient.fetchHealth();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Painel de Integrações')),
      body: FutureBuilder<List<HealthStatus>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return _ErrorState(error: snapshot.error, onRetry: _reload);
          }

          final items = snapshot.data ?? const [];
          if (items.isEmpty) {
            return const Center(child: Text('Nenhuma integração configurada.'));
          }

          return RefreshIndicator(
            onRefresh: () async => _reload(),
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: items.length,
              itemBuilder: (context, index) => _HealthCard(status: items[index]),
            ),
          );
        },
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.error, required this.onRetry});

  final Object? error;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 40),
            const SizedBox(height: 12),
            Text(
              'Não foi possível carregar o painel.\n$error',
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: onRetry, child: const Text('Tentar novamente')),
          ],
        ),
      ),
    );
  }
}

class _HealthCard extends StatelessWidget {
  const _HealthCard({required this.status});

  final HealthStatus status;

  @override
  Widget build(BuildContext context) {
    final statusColor = status.isResponding ? Colors.green : Colors.red;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.circle, color: statusColor, size: 12),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    status.label,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                Text(status.isResponding ? 'Respondendo' : 'Não respondendo'),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Última sincronização bem-sucedida: '
              '${_formatDateTime(status.lastSuccessfulSync)}',
            ),
            Text('Registros: ${status.recordsCount}'),
            if (status.lastError != null) ...[
              const SizedBox(height: 8),
              Text(
                'Último erro (${_formatDateTime(status.lastErrorAt)}): '
                '${status.lastError}',
                style: const TextStyle(color: Colors.red),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatDateTime(DateTime? value) {
    if (value == null) return 'nunca';
    final local = value.toLocal();
    String twoDigits(int n) => n.toString().padLeft(2, '0');
    return '${twoDigits(local.day)}/${twoDigits(local.month)}/${local.year} '
        '${twoDigits(local.hour)}:${twoDigits(local.minute)}';
  }
}
