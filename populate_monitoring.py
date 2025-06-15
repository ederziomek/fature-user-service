#!/usr/bin/env python3
"""
Script para popular banco com métricas de exemplo e regras de alerta
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
import json
import random

from src.main import app
from src.models.metrics import (
    db, BusinessMetric, AlertRule, ServiceHealth, 
    MetricType, MetricFrequency
)

def create_sample_metrics():
    """Cria métricas de exemplo"""
    print("Criando métricas de exemplo...")
    
    # Métricas de receita
    base_date = datetime.utcnow() - timedelta(days=7)
    
    for i in range(168):  # 7 dias * 24 horas
        timestamp = base_date + timedelta(hours=i)
        
        # Receita horária
        revenue = random.uniform(1000, 5000)
        metric = BusinessMetric(
            metric_name='revenue_hourly',
            metric_type=MetricType.REVENUE,
            value=revenue,
            unit='BRL',
            frequency=MetricFrequency.HOURLY,
            service_name='payment-service',
            region='BR',
            timestamp=timestamp
        )
        db.session.add(metric)
        
        # Comissões pagas
        commission = revenue * random.uniform(0.05, 0.15)
        metric = BusinessMetric(
            metric_name='commission_paid',
            metric_type=MetricType.COMMISSION,
            value=commission,
            unit='BRL',
            frequency=MetricFrequency.HOURLY,
            service_name='commission-service',
            timestamp=timestamp
        )
        db.session.add(metric)
        
        # Usuários ativos
        active_users = random.randint(50, 200)
        metric = BusinessMetric(
            metric_name='active_users',
            metric_type=MetricType.USER_ACTIVITY,
            value=active_users,
            unit='count',
            frequency=MetricFrequency.HOURLY,
            service_name='user-service',
            timestamp=timestamp
        )
        db.session.add(metric)
        
        # Taxa de conversão
        conversion_rate = random.uniform(0.02, 0.08)
        metric = BusinessMetric(
            metric_name='conversion_rate',
            metric_type=MetricType.CONVERSION,
            value=conversion_rate,
            unit='%',
            frequency=MetricFrequency.HOURLY,
            service_name='user-service',
            timestamp=timestamp
        )
        db.session.add(metric)
        
        # Tempo de resposta da API
        response_time = random.uniform(50, 300)
        metric = BusinessMetric(
            metric_name='api_response_time',
            metric_type=MetricType.PERFORMANCE,
            value=response_time,
            unit='ms',
            frequency=MetricFrequency.HOURLY,
            service_name='api-gateway',
            timestamp=timestamp
        )
        db.session.add(metric)
        
        # Baús abertos
        chests_opened = random.randint(20, 100)
        metric = BusinessMetric(
            metric_name='chests_opened',
            metric_type=MetricType.GAMIFICATION,
            value=chests_opened,
            unit='count',
            frequency=MetricFrequency.HOURLY,
            service_name='gamification-service',
            timestamp=timestamp
        )
        db.session.add(metric)
        
        # Validações de indicação
        validations = random.randint(10, 50)
        metric = BusinessMetric(
            metric_name='indication_validations',
            metric_type=MetricType.VALIDATION,
            value=validations,
            unit='count',
            frequency=MetricFrequency.HOURLY,
            service_name='validation-service',
            timestamp=timestamp
        )
        db.session.add(metric)
    
    print(f"Criadas {168 * 7} métricas de exemplo")

def create_alert_rules():
    """Cria regras de alerta padrão"""
    print("Criando regras de alerta...")
    
    rules = [
        {
            'rule_name': 'Low Revenue Alert',
            'metric_name': 'revenue_hourly',
            'condition': '<',
            'threshold_value': 1500.0,
            'severity': 'medium',
            'notification_channels': ['email', 'slack'],
            'notification_recipients': ['admin@fature.com', 'finance@fature.com']
        },
        {
            'rule_name': 'High API Response Time',
            'metric_name': 'api_response_time',
            'condition': '>',
            'threshold_value': 250.0,
            'severity': 'high',
            'notification_channels': ['slack', 'webhook'],
            'notification_recipients': ['devops@fature.com']
        },
        {
            'rule_name': 'Low Conversion Rate',
            'metric_name': 'conversion_rate',
            'condition': '<',
            'threshold_value': 0.03,
            'severity': 'medium',
            'notification_channels': ['email'],
            'notification_recipients': ['marketing@fature.com']
        },
        {
            'rule_name': 'High Commission Payout',
            'metric_name': 'commission_paid',
            'condition': '>',
            'threshold_value': 500.0,
            'severity': 'low',
            'notification_channels': ['email'],
            'notification_recipients': ['finance@fature.com']
        },
        {
            'rule_name': 'Low Active Users',
            'metric_name': 'active_users',
            'condition': '<',
            'threshold_value': 75,
            'severity': 'medium',
            'notification_channels': ['email', 'slack'],
            'notification_recipients': ['product@fature.com']
        }
    ]
    
    for rule_data in rules:
        rule = AlertRule(
            rule_name=rule_data['rule_name'],
            metric_name=rule_data['metric_name'],
            condition=rule_data['condition'],
            threshold_value=rule_data['threshold_value'],
            severity=rule_data['severity'],
            notification_channels=json.dumps(rule_data['notification_channels']),
            notification_recipients=json.dumps(rule_data['notification_recipients']),
            is_active=True
        )
        db.session.add(rule)
    
    print(f"Criadas {len(rules)} regras de alerta")

def create_service_health():
    """Cria registros de saúde dos serviços"""
    print("Criando registros de saúde dos serviços...")
    
    services = [
        'user-service',
        'payment-service',
        'commission-service',
        'gamification-service',
        'validation-service',
        'integration-service',
        'config-service',
        'api-gateway'
    ]
    
    for service in services:
        # Status atual (saudável)
        health = ServiceHealth(
            service_name=service,
            status='healthy',
            response_time_ms=random.uniform(20, 100),
            error_rate=random.uniform(0.001, 0.01),
            cpu_usage=random.uniform(0.1, 0.6),
            memory_usage=random.uniform(0.2, 0.7),
            version='1.0.0',
            uptime_seconds=random.randint(3600, 86400),
            timestamp=datetime.utcnow()
        )
        db.session.add(health)
        
        # Histórico das últimas 24 horas
        for i in range(24):
            timestamp = datetime.utcnow() - timedelta(hours=i)
            
            # Simula alguns problemas ocasionais
            if random.random() < 0.05:  # 5% chance de problema
                status = 'degraded'
                response_time = random.uniform(200, 500)
                error_rate = random.uniform(0.05, 0.15)
            else:
                status = 'healthy'
                response_time = random.uniform(20, 100)
                error_rate = random.uniform(0.001, 0.01)
            
            health = ServiceHealth(
                service_name=service,
                status=status,
                response_time_ms=response_time,
                error_rate=error_rate,
                cpu_usage=random.uniform(0.1, 0.8),
                memory_usage=random.uniform(0.2, 0.8),
                version='1.0.0',
                uptime_seconds=random.randint(3600, 86400),
                timestamp=timestamp
            )
            db.session.add(health)
    
    print(f"Criados registros de saúde para {len(services)} serviços")

def main():
    """Função principal"""
    print("=== Populando banco de dados do sistema de monitoramento ===")
    
    with app.app_context():
        # Limpa dados existentes
        print("Limpando dados existentes...")
        BusinessMetric.query.delete()
        AlertRule.query.delete()
        ServiceHealth.query.delete()
        
        # Cria dados de exemplo
        create_sample_metrics()
        create_alert_rules()
        create_service_health()
        
        # Salva no banco
        db.session.commit()
        
        print("\n=== Resumo dos dados criados ===")
        print(f"Métricas de negócio: {BusinessMetric.query.count()}")
        print(f"Regras de alerta: {AlertRule.query.count()}")
        print(f"Registros de saúde: {ServiceHealth.query.count()}")
        
        print("\n✅ Banco de dados populado com sucesso!")
        
        # Mostra algumas estatísticas
        print("\n=== Estatísticas das métricas ===")
        
        # Receita total dos últimos 7 dias
        total_revenue = db.session.query(
            db.func.sum(BusinessMetric.value)
        ).filter(
            BusinessMetric.metric_name == 'revenue_hourly'
        ).scalar()
        
        print(f"Receita total (7 dias): R$ {total_revenue:,.2f}")
        
        # Comissões pagas
        total_commission = db.session.query(
            db.func.sum(BusinessMetric.value)
        ).filter(
            BusinessMetric.metric_name == 'commission_paid'
        ).scalar()
        
        print(f"Comissões pagas (7 dias): R$ {total_commission:,.2f}")
        
        # Taxa de conversão média
        avg_conversion = db.session.query(
            db.func.avg(BusinessMetric.value)
        ).filter(
            BusinessMetric.metric_name == 'conversion_rate'
        ).scalar()
        
        print(f"Taxa de conversão média: {avg_conversion:.2%}")
        
        # Tempo de resposta médio
        avg_response_time = db.session.query(
            db.func.avg(BusinessMetric.value)
        ).filter(
            BusinessMetric.metric_name == 'api_response_time'
        ).scalar()
        
        print(f"Tempo de resposta médio: {avg_response_time:.1f}ms")

if __name__ == '__main__':
    main()

