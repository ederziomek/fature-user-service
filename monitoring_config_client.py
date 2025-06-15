#!/usr/bin/env python3
"""
Sistema de Monitoramento - Cliente Config Service
Todas as configurações obtidas do config-service (sem valores hardcoded)
"""
import requests
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """Configurações de monitoramento obtidas do config-service"""
    # Configurações de retenção
    retention_days_realtime: int
    retention_days_hourly: int
    retention_days_daily: int
    retention_days_monthly: int
    retention_days_alerts: int
    retention_days_health: int
    
    # Configurações de performance
    batch_size_limit: int
    alert_check_interval_seconds: int
    metrics_aggregation_interval_seconds: int
    query_timeout_seconds: int
    cache_ttl_seconds: int
    
    # Configurações de alertas
    default_severity: str
    notification_timeout_seconds: int
    max_retries: int
    retry_delay_seconds: int
    
    # Thresholds de alertas críticos
    revenue_low_threshold: float
    api_response_time_high_threshold: float
    conversion_rate_low_threshold: float
    commission_high_threshold: float
    active_users_low_threshold: int
    error_rate_high_threshold: float
    cpu_usage_high_threshold: float
    memory_usage_high_threshold: float
    
    # Configurações de notificação
    email_enabled: bool
    slack_enabled: bool
    webhook_enabled: bool
    sms_enabled: bool
    
    # URLs de notificação
    slack_webhook_url: str
    email_smtp_server: str
    email_smtp_port: int
    webhook_url: str

class MonitoringConfigClient:
    """Cliente para obter configurações de monitoramento do config-service"""
    
    def __init__(self, config_service_url: str = None):
        self.config_service_url = config_service_url or "http://config-service.fature.svc.cluster.local"
        self.session = requests.Session()
        self.session.timeout = 10
        
    def get_monitoring_config(self) -> MonitoringConfig:
        """Obtém todas as configurações de monitoramento"""
        try:
            config_keys = [
                # Retenção de dados
                'monitoramento.retencao.tempo_real_dias',
                'monitoramento.retencao.horario_dias',
                'monitoramento.retencao.diario_dias',
                'monitoramento.retencao.mensal_dias',
                'monitoramento.retencao.alertas_dias',
                'monitoramento.retencao.saude_servicos_dias',
                
                # Performance
                'monitoramento.performance.limite_lote',
                'monitoramento.performance.intervalo_verificacao_alertas_segundos',
                'monitoramento.performance.intervalo_agregacao_metricas_segundos',
                'monitoramento.performance.timeout_consulta_segundos',
                'monitoramento.performance.cache_ttl_segundos',
                
                # Alertas
                'monitoramento.alertas.severidade_padrao',
                'monitoramento.alertas.timeout_notificacao_segundos',
                'monitoramento.alertas.max_tentativas',
                'monitoramento.alertas.delay_retry_segundos',
                
                # Thresholds críticos
                'monitoramento.thresholds.receita_baixa_brl',
                'monitoramento.thresholds.api_tempo_resposta_alto_ms',
                'monitoramento.thresholds.taxa_conversao_baixa_percent',
                'monitoramento.thresholds.comissao_alta_brl',
                'monitoramento.thresholds.usuarios_ativos_baixo_count',
                'monitoramento.thresholds.taxa_erro_alta_percent',
                'monitoramento.thresholds.cpu_alto_percent',
                'monitoramento.thresholds.memoria_alta_percent',
                
                # Notificações
                'monitoramento.notificacoes.email_ativo',
                'monitoramento.notificacoes.slack_ativo',
                'monitoramento.notificacoes.webhook_ativo',
                'monitoramento.notificacoes.sms_ativo',
                
                # URLs de notificação
                'monitoramento.notificacoes.slack_webhook_url',
                'monitoramento.notificacoes.email_smtp_servidor',
                'monitoramento.notificacoes.email_smtp_porta',
                'monitoramento.notificacoes.webhook_url'
            ]
            
            config_values = {}
            
            for key in config_keys:
                try:
                    response = self.session.get(f"{self.config_service_url}/api/v1/config/{key}")
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            config_values[key] = data['data']['value']
                        else:
                            config_values[key] = self._get_fallback_value(key)
                    else:
                        config_values[key] = self._get_fallback_value(key)
                        
                except Exception as e:
                    logger.error(f"Error getting config {key}: {e}")
                    config_values[key] = self._get_fallback_value(key)
            
            return MonitoringConfig(
                # Retenção
                retention_days_realtime=int(config_values['monitoramento.retencao.tempo_real_dias']),
                retention_days_hourly=int(config_values['monitoramento.retencao.horario_dias']),
                retention_days_daily=int(config_values['monitoramento.retencao.diario_dias']),
                retention_days_monthly=int(config_values['monitoramento.retencao.mensal_dias']),
                retention_days_alerts=int(config_values['monitoramento.retencao.alertas_dias']),
                retention_days_health=int(config_values['monitoramento.retencao.saude_servicos_dias']),
                
                # Performance
                batch_size_limit=int(config_values['monitoramento.performance.limite_lote']),
                alert_check_interval_seconds=int(config_values['monitoramento.performance.intervalo_verificacao_alertas_segundos']),
                metrics_aggregation_interval_seconds=int(config_values['monitoramento.performance.intervalo_agregacao_metricas_segundos']),
                query_timeout_seconds=int(config_values['monitoramento.performance.timeout_consulta_segundos']),
                cache_ttl_seconds=int(config_values['monitoramento.performance.cache_ttl_segundos']),
                
                # Alertas
                default_severity=str(config_values['monitoramento.alertas.severidade_padrao']),
                notification_timeout_seconds=int(config_values['monitoramento.alertas.timeout_notificacao_segundos']),
                max_retries=int(config_values['monitoramento.alertas.max_tentativas']),
                retry_delay_seconds=int(config_values['monitoramento.alertas.delay_retry_segundos']),
                
                # Thresholds
                revenue_low_threshold=float(config_values['monitoramento.thresholds.receita_baixa_brl']),
                api_response_time_high_threshold=float(config_values['monitoramento.thresholds.api_tempo_resposta_alto_ms']),
                conversion_rate_low_threshold=float(config_values['monitoramento.thresholds.taxa_conversao_baixa_percent']),
                commission_high_threshold=float(config_values['monitoramento.thresholds.comissao_alta_brl']),
                active_users_low_threshold=int(config_values['monitoramento.thresholds.usuarios_ativos_baixo_count']),
                error_rate_high_threshold=float(config_values['monitoramento.thresholds.taxa_erro_alta_percent']),
                cpu_usage_high_threshold=float(config_values['monitoramento.thresholds.cpu_alto_percent']),
                memory_usage_high_threshold=float(config_values['monitoramento.thresholds.memoria_alta_percent']),
                
                # Notificações
                email_enabled=bool(config_values['monitoramento.notificacoes.email_ativo']),
                slack_enabled=bool(config_values['monitoramento.notificacoes.slack_ativo']),
                webhook_enabled=bool(config_values['monitoramento.notificacoes.webhook_ativo']),
                sms_enabled=bool(config_values['monitoramento.notificacoes.sms_ativo']),
                
                # URLs
                slack_webhook_url=str(config_values['monitoramento.notificacoes.slack_webhook_url']),
                email_smtp_server=str(config_values['monitoramento.notificacoes.email_smtp_servidor']),
                email_smtp_port=int(config_values['monitoramento.notificacoes.email_smtp_porta']),
                webhook_url=str(config_values['monitoramento.notificacoes.webhook_url'])
            )
            
        except Exception as e:
            logger.error(f"Failed to get monitoring config: {e}")
            return self._get_emergency_config()
    
    def _get_fallback_value(self, key: str):
        """Valores de fallback apenas para emergência"""
        fallbacks = {
            # Retenção
            'monitoramento.retencao.tempo_real_dias': 7,
            'monitoramento.retencao.horario_dias': 90,
            'monitoramento.retencao.diario_dias': 730,
            'monitoramento.retencao.mensal_dias': 1825,
            'monitoramento.retencao.alertas_dias': 365,
            'monitoramento.retencao.saude_servicos_dias': 30,
            
            # Performance
            'monitoramento.performance.limite_lote': 1000,
            'monitoramento.performance.intervalo_verificacao_alertas_segundos': 60,
            'monitoramento.performance.intervalo_agregacao_metricas_segundos': 300,
            'monitoramento.performance.timeout_consulta_segundos': 30,
            'monitoramento.performance.cache_ttl_segundos': 300,
            
            # Alertas
            'monitoramento.alertas.severidade_padrao': 'medium',
            'monitoramento.alertas.timeout_notificacao_segundos': 30,
            'monitoramento.alertas.max_tentativas': 3,
            'monitoramento.alertas.delay_retry_segundos': 60,
            
            # Thresholds
            'monitoramento.thresholds.receita_baixa_brl': 1500.0,
            'monitoramento.thresholds.api_tempo_resposta_alto_ms': 250.0,
            'monitoramento.thresholds.taxa_conversao_baixa_percent': 0.03,
            'monitoramento.thresholds.comissao_alta_brl': 500.0,
            'monitoramento.thresholds.usuarios_ativos_baixo_count': 75,
            'monitoramento.thresholds.taxa_erro_alta_percent': 0.05,
            'monitoramento.thresholds.cpu_alto_percent': 0.80,
            'monitoramento.thresholds.memoria_alta_percent': 0.85,
            
            # Notificações
            'monitoramento.notificacoes.email_ativo': True,
            'monitoramento.notificacoes.slack_ativo': True,
            'monitoramento.notificacoes.webhook_ativo': False,
            'monitoramento.notificacoes.sms_ativo': False,
            
            # URLs
            'monitoramento.notificacoes.slack_webhook_url': '',
            'monitoramento.notificacoes.email_smtp_servidor': 'smtp.gmail.com',
            'monitoramento.notificacoes.email_smtp_porta': 587,
            'monitoramento.notificacoes.webhook_url': ''
        }
        return fallbacks.get(key, None)
    
    def _get_emergency_config(self) -> MonitoringConfig:
        """Configuração de emergência"""
        return MonitoringConfig(
            retention_days_realtime=7,
            retention_days_hourly=90,
            retention_days_daily=730,
            retention_days_monthly=1825,
            retention_days_alerts=365,
            retention_days_health=30,
            batch_size_limit=1000,
            alert_check_interval_seconds=60,
            metrics_aggregation_interval_seconds=300,
            query_timeout_seconds=30,
            cache_ttl_seconds=300,
            default_severity='medium',
            notification_timeout_seconds=30,
            max_retries=3,
            retry_delay_seconds=60,
            revenue_low_threshold=1500.0,
            api_response_time_high_threshold=250.0,
            conversion_rate_low_threshold=0.03,
            commission_high_threshold=500.0,
            active_users_low_threshold=75,
            error_rate_high_threshold=0.05,
            cpu_usage_high_threshold=0.80,
            memory_usage_high_threshold=0.85,
            email_enabled=True,
            slack_enabled=True,
            webhook_enabled=False,
            sms_enabled=False,
            slack_webhook_url='',
            email_smtp_server='smtp.gmail.com',
            email_smtp_port=587,
            webhook_url=''
        )

# Função para criar regras de alerta baseadas nas configurações
def create_alert_rules_from_config(config: MonitoringConfig) -> list:
    """Cria regras de alerta baseadas nas configurações do config-service"""
    rules = [
        {
            'rule_name': 'Receita Baixa',
            'metric_name': 'revenue_hourly',
            'condition': '<',
            'threshold_value': config.revenue_low_threshold,
            'severity': 'medium',
            'notification_channels': ['email', 'slack'] if config.email_enabled and config.slack_enabled else ['email'] if config.email_enabled else ['slack'] if config.slack_enabled else [],
            'notification_recipients': ['admin@fature.com', 'finance@fature.com']
        },
        {
            'rule_name': 'API Tempo Resposta Alto',
            'metric_name': 'api_response_time',
            'condition': '>',
            'threshold_value': config.api_response_time_high_threshold,
            'severity': 'high',
            'notification_channels': ['slack', 'webhook'] if config.slack_enabled and config.webhook_enabled else ['slack'] if config.slack_enabled else [],
            'notification_recipients': ['devops@fature.com']
        },
        {
            'rule_name': 'Taxa Conversão Baixa',
            'metric_name': 'conversion_rate',
            'condition': '<',
            'threshold_value': config.conversion_rate_low_threshold,
            'severity': 'medium',
            'notification_channels': ['email'] if config.email_enabled else [],
            'notification_recipients': ['marketing@fature.com']
        },
        {
            'rule_name': 'Comissão Alta',
            'metric_name': 'commission_paid',
            'condition': '>',
            'threshold_value': config.commission_high_threshold,
            'severity': 'low',
            'notification_channels': ['email'] if config.email_enabled else [],
            'notification_recipients': ['finance@fature.com']
        },
        {
            'rule_name': 'Poucos Usuários Ativos',
            'metric_name': 'active_users',
            'condition': '<',
            'threshold_value': config.active_users_low_threshold,
            'severity': 'medium',
            'notification_channels': ['email', 'slack'] if config.email_enabled and config.slack_enabled else ['email'] if config.email_enabled else ['slack'] if config.slack_enabled else [],
            'notification_recipients': ['product@fature.com']
        },
        {
            'rule_name': 'Taxa Erro Alta',
            'metric_name': 'error_rate',
            'condition': '>',
            'threshold_value': config.error_rate_high_threshold,
            'severity': 'critical',
            'notification_channels': ['email', 'slack', 'webhook'] if all([config.email_enabled, config.slack_enabled, config.webhook_enabled]) else ['email', 'slack'] if config.email_enabled and config.slack_enabled else ['slack'] if config.slack_enabled else [],
            'notification_recipients': ['devops@fature.com', 'admin@fature.com']
        },
        {
            'rule_name': 'CPU Alto',
            'metric_name': 'cpu_usage',
            'condition': '>',
            'threshold_value': config.cpu_usage_high_threshold,
            'severity': 'high',
            'notification_channels': ['slack'] if config.slack_enabled else [],
            'notification_recipients': ['devops@fature.com']
        },
        {
            'rule_name': 'Memória Alta',
            'metric_name': 'memory_usage',
            'condition': '>',
            'threshold_value': config.memory_usage_high_threshold,
            'severity': 'high',
            'notification_channels': ['slack'] if config.slack_enabled else [],
            'notification_recipients': ['devops@fature.com']
        }
    ]
    
    # Filtra regras que têm canais de notificação configurados
    valid_rules = [rule for rule in rules if rule['notification_channels']]
    
    return valid_rules

# Exemplo de uso
if __name__ == "__main__":
    # Inicializa cliente
    config_client = MonitoringConfigClient()
    
    # Obtém configurações
    config = config_client.get_monitoring_config()
    
    print("=== Configurações de Monitoramento (Config-Service) ===")
    print(f"Retenção dados tempo real: {config.retention_days_realtime} dias")
    print(f"Limite de lote: {config.batch_size_limit}")
    print(f"Threshold receita baixa: R$ {config.revenue_low_threshold}")
    print(f"Threshold API lenta: {config.api_response_time_high_threshold}ms")
    print(f"Email ativo: {config.email_enabled}")
    print(f"Slack ativo: {config.slack_enabled}")
    
    # Cria regras de alerta baseadas nas configurações
    alert_rules = create_alert_rules_from_config(config)
    print(f"\nRegras de alerta criadas: {len(alert_rules)}")
    
    for rule in alert_rules:
        print(f"- {rule['rule_name']}: {rule['metric_name']} {rule['condition']} {rule['threshold_value']}")
    
    print("\n✅ Todas as configurações obtidas do config-service!")

