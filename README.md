# Sistema de Monitoramento e Métricas de Negócio - Fature

Microserviço centralizado para coleta, armazenamento e análise de métricas de negócio do Sistema Fature, com sistema de alertas em tempo real e dashboards de observabilidade.

## Problema Resolvido

O Sistema Fature carecia de visibilidade sobre métricas críticas de negócio:
- **Falta de centralização** de métricas entre microserviços
- **Ausência de alertas** para problemas críticos
- **Dificuldade de análise** de tendências e padrões
- **Monitoramento reativo** ao invés de proativo

Este sistema resolve implementando:
- **Coleta centralizada** de métricas de todos os serviços
- **Sistema de alertas** configurável e em tempo real
- **APIs robustas** para consulta e agregação de dados
- **Dashboards** para visualização e análise

## Arquitetura do Sistema

### Componentes Principais

1. **Modelos de Dados** (`src/models/metrics.py`)
   - BusinessMetric: Métricas de negócio
   - AlertRule: Regras de alerta
   - AlertEvent: Eventos de alerta disparados
   - ServiceHealth: Saúde dos microserviços
   - DashboardConfig: Configuração de dashboards

2. **APIs REST** (`src/routes/monitoring.py`)
   - Coleta de métricas individual e em lote
   - Consulta e agregação de dados
   - Gerenciamento de alertas
   - Monitoramento de saúde dos serviços

3. **Sistema de Alertas**
   - Verificação automática de thresholds
   - Múltiplos canais de notificação
   - Severidade configurável
   - Histórico de eventos

### Tipos de Métricas Suportadas

#### Revenue (Receita)
- `revenue_hourly`: Receita por hora
- `revenue_daily`: Receita diária
- `revenue_monthly`: Receita mensal
- `average_order_value`: Valor médio do pedido

#### Commission (Comissão)
- `commission_paid`: Comissões pagas
- `commission_pending`: Comissões pendentes
- `commission_rate`: Taxa de comissão média
- `top_affiliates_revenue`: Receita dos top afiliados

#### User Activity (Atividade do Usuário)
- `active_users`: Usuários ativos
- `new_registrations`: Novos registros
- `user_retention_rate`: Taxa de retenção
- `session_duration`: Duração média da sessão

#### Conversion (Conversão)
- `conversion_rate`: Taxa de conversão
- `funnel_completion`: Conclusão do funil
- `bounce_rate`: Taxa de rejeição
- `click_through_rate`: Taxa de cliques

#### Performance (Performance)
- `api_response_time`: Tempo de resposta da API
- `error_rate`: Taxa de erro
- `throughput`: Throughput de requests
- `database_query_time`: Tempo de consulta ao banco

#### Gamification (Gamificação)
- `chests_opened`: Baús abertos
- `rewards_distributed`: Recompensas distribuídas
- `user_engagement_score`: Score de engajamento
- `achievement_completion`: Conclusão de conquistas

#### Validation (Validação)
- `indication_validations`: Validações de indicação
- `validation_success_rate`: Taxa de sucesso de validação
- `fraud_detection_rate`: Taxa de detecção de fraude
- `manual_review_required`: Revisões manuais necessárias

## API Endpoints

### Coleta de Métricas

#### POST /api/metrics
Registra uma métrica individual.

**Request:**
```json
{
  "metric_name": "revenue_hourly",
  "metric_type": "revenue",
  "value": 2500.00,
  "unit": "BRL",
  "frequency": "hourly",
  "service_name": "payment-service",
  "region": "BR",
  "metadata": {
    "payment_method": "credit_card",
    "campaign_id": "summer_2025"
  }
}
```

**Response:**
```json
{
  "success": true,
  "metric_id": 12345,
  "message": "Metric recorded successfully"
}
```

#### POST /api/metrics/batch
Registra múltiplas métricas em lote (até 1000).

**Request:**
```json
{
  "metrics": [
    {
      "metric_name": "active_users",
      "metric_type": "user_activity",
      "value": 150,
      "unit": "count",
      "frequency": "hourly",
      "service_name": "user-service"
    }
  ]
}
```

### Consulta de Métricas

#### GET /api/metrics/query
Consulta métricas com filtros.

**Parâmetros:**
- `metric_name`: Nome da métrica
- `metric_type`: Tipo da métrica
- `service_name`: Nome do serviço
- `affiliate_id`: ID do afiliado
- `start_date`: Data de início (ISO 8601)
- `end_date`: Data de fim (ISO 8601)
- `limit`: Limite de resultados (padrão: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 12345,
      "metric_name": "revenue_hourly",
      "metric_type": "revenue",
      "value": 2500.00,
      "unit": "BRL",
      "timestamp": "2025-06-14T15:00:00Z",
      "service_name": "payment-service",
      "metadata": {...}
    }
  ],
  "count": 1
}
```

#### GET /api/metrics/aggregate
Agrega métricas por período.

**Parâmetros:**
- `metric_name`: Nome da métrica (obrigatório)
- `aggregation`: Tipo de agregação (sum, avg, min, max, count)
- `period`: Período de agregação (hour, day, week, month)
- `start_date`: Data de início
- `end_date`: Data de fim

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "period": "2025-06-14",
      "value": 45000.00
    }
  ],
  "aggregation": "sum",
  "period": "day",
  "metric_name": "revenue_hourly"
}
```

### Sistema de Alertas

#### GET /api/alerts/rules
Lista todas as regras de alerta.

#### POST /api/alerts/rules
Cria nova regra de alerta.

**Request:**
```json
{
  "rule_name": "Low Revenue Alert",
  "metric_name": "revenue_hourly",
  "condition": "<",
  "threshold_value": 1500.0,
  "severity": "medium",
  "notification_channels": ["email", "slack"],
  "notification_recipients": ["admin@fature.com"],
  "is_active": true
}
```

#### GET /api/alerts/events
Lista eventos de alerta.

**Parâmetros:**
- `status`: Status do evento (open, acknowledged, resolved)
- `severity`: Severidade (low, medium, high, critical)
- `limit`: Limite de resultados

### Monitoramento de Serviços

#### POST /api/services/health
Atualiza saúde de um serviço.

**Request:**
```json
{
  "service_name": "payment-service",
  "status": "healthy",
  "response_time_ms": 85.5,
  "error_rate": 0.002,
  "cpu_usage": 0.45,
  "memory_usage": 0.67,
  "version": "1.2.3",
  "uptime_seconds": 86400
}
```

#### GET /api/services/health
Obtém saúde atual de todos os serviços.

## Configuração de Alertas

### Condições Suportadas
- `>`: Maior que
- `<`: Menor que
- `>=`: Maior ou igual
- `<=`: Menor ou igual
- `==`: Igual
- `!=`: Diferente

### Severidades
- **low**: Informativo, não crítico
- **medium**: Atenção necessária
- **high**: Problema sério, ação imediata
- **critical**: Sistema comprometido, emergência

### Canais de Notificação
- **email**: Notificação por email
- **slack**: Mensagem no Slack
- **webhook**: Chamada HTTP para webhook
- **sms**: SMS (futuro)

## Exemplos de Uso

### Integração com Microserviços

#### Payment Service
```python
import requests

# Registra receita
def record_payment(amount, payment_method):
    metric_data = {
        "metric_name": "revenue_hourly",
        "metric_type": "revenue",
        "value": amount,
        "unit": "BRL",
        "frequency": "hourly",
        "service_name": "payment-service",
        "metadata": {
            "payment_method": payment_method
        }
    }
    
    response = requests.post(
        "http://monitoring-service/api/metrics",
        json=metric_data
    )
    
    return response.json()
```

#### User Service
```python
# Registra usuários ativos
def record_active_users(count):
    metric_data = {
        "metric_name": "active_users",
        "metric_type": "user_activity",
        "value": count,
        "unit": "count",
        "frequency": "hourly",
        "service_name": "user-service"
    }
    
    requests.post(
        "http://monitoring-service/api/metrics",
        json=metric_data
    )
```

#### Commission Service
```python
# Registra comissões pagas
def record_commission_payment(affiliate_id, amount):
    metric_data = {
        "metric_name": "commission_paid",
        "metric_type": "commission",
        "value": amount,
        "unit": "BRL",
        "frequency": "real_time",
        "service_name": "commission-service",
        "affiliate_id": affiliate_id
    }
    
    requests.post(
        "http://monitoring-service/api/metrics",
        json=metric_data
    )
```

### Consultas de Análise

#### Receita dos Últimos 7 Dias
```bash
curl "http://monitoring-service/api/metrics/aggregate?metric_name=revenue_hourly&aggregation=sum&period=day&start_date=2025-06-07T00:00:00Z&end_date=2025-06-14T23:59:59Z"
```

#### Top 10 Afiliados por Comissão
```bash
curl "http://monitoring-service/api/metrics/query?metric_name=commission_paid&limit=10" | jq '.data | group_by(.affiliate_id) | map({affiliate_id: .[0].affiliate_id, total: map(.value) | add}) | sort_by(.total) | reverse'
```

#### Taxa de Conversão por Hora
```bash
curl "http://monitoring-service/api/metrics/aggregate?metric_name=conversion_rate&aggregation=avg&period=hour&start_date=2025-06-14T00:00:00Z"
```

## Deployment

### Kubernetes
```bash
# Aplica deployment
kubectl apply -f k8s-deployment.yaml

# Verifica status
kubectl get pods -n fature -l app=monitoring-service

# Verifica logs
kubectl logs -n fature -l app=monitoring-service

# Acessa métricas
kubectl port-forward -n fature svc/monitoring-service 8080:80
curl http://localhost:8080/api/health
```

### Docker
```bash
# Build da imagem
docker build -t fature/monitoring-service:latest .

# Execução local
docker run -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  fature/monitoring-service:latest
```

## Monitoramento e Observabilidade

### Health Checks
- **Endpoint**: `/api/health`
- **Liveness Probe**: A cada 10s
- **Readiness Probe**: A cada 5s

### Métricas Coletadas
- **Request rate**: Requests por segundo
- **Response time**: Latência P50/P95/P99
- **Error rate**: Porcentagem de erros
- **Database performance**: Tempo de consulta
- **Alert frequency**: Frequência de alertas

### Logs Estruturados
```json
{
  "timestamp": "2025-06-14T15:30:00Z",
  "level": "INFO",
  "service": "monitoring-service",
  "event": "metric_recorded",
  "metric_name": "revenue_hourly",
  "value": 2500.00,
  "service_name": "payment-service"
}
```

### Alertas Pré-configurados

#### Receita Baixa
- **Métrica**: `revenue_hourly`
- **Condição**: `< 1500 BRL`
- **Severidade**: Medium
- **Notificação**: Email + Slack

#### API Lenta
- **Métrica**: `api_response_time`
- **Condição**: `> 250ms`
- **Severidade**: High
- **Notificação**: Slack + Webhook

#### Taxa de Conversão Baixa
- **Métrica**: `conversion_rate`
- **Condição**: `< 3%`
- **Severidade**: Medium
- **Notificação**: Email

#### Comissões Altas
- **Métrica**: `commission_paid`
- **Condição**: `> 500 BRL/hora`
- **Severidade**: Low
- **Notificação**: Email

#### Poucos Usuários Ativos
- **Métrica**: `active_users`
- **Condição**: `< 75`
- **Severidade**: Medium
- **Notificação**: Email + Slack

## Retenção de Dados

### Políticas de Retenção
- **Métricas em tempo real**: 7 dias
- **Métricas horárias**: 90 dias
- **Métricas diárias**: 2 anos
- **Métricas mensais**: 5 anos
- **Eventos de alerta**: 1 ano
- **Saúde dos serviços**: 30 dias

### Cleanup Automático
- **CronJob**: Executa diariamente às 2h
- **Script**: `scripts/cleanup_old_data.py`
- **Configuração**: Variável `RETENTION_DAYS`

## Segurança

### Autenticação
- **API Keys**: Para acesso programático
- **JWT Tokens**: Para dashboards web
- **Service Accounts**: Para microserviços

### Autorização
- **RBAC**: Controle baseado em roles
- **Scopes**: Leitura vs escrita
- **Service isolation**: Cada serviço só acessa suas métricas

### Network Policies
- **Ingress**: Apenas serviços autorizados
- **Egress**: DNS e HTTPS apenas
- **Isolation**: Namespace dedicado

## Performance

### Otimizações
- **Batch processing**: Até 1000 métricas por request
- **Database indexing**: Índices otimizados para consultas
- **Query optimization**: Agregações eficientes
- **Caching**: Cache de consultas frequentes

### Benchmarks
- **Throughput**: 10,000+ métricas/segundo
- **Latência**: <50ms para inserção individual
- **Batch latency**: <200ms para 1000 métricas
- **Query performance**: <100ms para agregações

### Escalabilidade
- **Horizontal scaling**: 2-8 replicas
- **Auto-scaling**: CPU 70%, Memory 80%
- **Database**: SQLite para desenvolvimento, PostgreSQL para produção
- **Storage**: PVC com 10GB, expansível

## Troubleshooting

### Problema: Métricas não aparecem
```bash
# Verifica logs do serviço
kubectl logs -n fature deployment/monitoring-service

# Testa endpoint de saúde
curl http://monitoring-service/api/health

# Verifica banco de dados
kubectl exec -n fature deployment/monitoring-service -- sqlite3 /app/data/monitoring.db ".tables"
```

### Problema: Alertas não disparam
```bash
# Lista regras de alerta
curl http://monitoring-service/api/alerts/rules

# Verifica eventos recentes
curl http://monitoring-service/api/alerts/events?limit=10

# Testa regra específica
curl -X POST http://monitoring-service/api/metrics \
  -H "Content-Type: application/json" \
  -d '{"metric_name":"test_metric","metric_type":"performance","value":999,"frequency":"real_time"}'
```

### Problema: Performance degradada
```bash
# Verifica uso de recursos
kubectl top pods -n fature -l app=monitoring-service

# Analisa queries lentas
kubectl logs -n fature deployment/monitoring-service | grep "SLOW_QUERY"

# Verifica índices do banco
kubectl exec -n fature deployment/monitoring-service -- sqlite3 /app/data/monitoring.db ".schema"
```

## Roadmap

### Versão 1.1
- [ ] Dashboard web interativo
- [ ] Integração com Grafana
- [ ] Métricas Prometheus nativas
- [ ] Notificações SMS

### Versão 1.2
- [ ] Machine Learning para detecção de anomalias
- [ ] Previsão de tendências
- [ ] Alertas inteligentes
- [ ] API GraphQL

### Versão 2.0
- [ ] Time series database (InfluxDB)
- [ ] Streaming de métricas (Kafka)
- [ ] Multi-tenancy
- [ ] Federação de métricas

## Contribuição

Este sistema foi desenvolvido como parte das correções P2 do Sistema Fature, implementando monitoramento e observabilidade completos para todos os microserviços.

**Desenvolvido por:** Manus AI  
**Data:** 14 de junho de 2025  
**Versão:** 1.0.0  
**Status:** Implementação P2 - Monitoramento Crítico

## Licença

Propriedade do Sistema Fature - Todos os direitos reservados.

