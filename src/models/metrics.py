#!/usr/bin/env python3
"""
Modelos de dados para métricas de negócio do Sistema Fature
"""
from src.models.user import db
from datetime import datetime
from enum import Enum
import json

class MetricType(Enum):
    """Tipos de métricas"""
    REVENUE = "revenue"
    COMMISSION = "commission"
    USER_ACTIVITY = "user_activity"
    CONVERSION = "conversion"
    PERFORMANCE = "performance"
    GAMIFICATION = "gamification"
    VALIDATION = "validation"

class MetricFrequency(Enum):
    """Frequência de coleta de métricas"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class BusinessMetric(db.Model):
    """Modelo para métricas de negócio"""
    __tablename__ = 'business_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False, index=True)
    metric_type = db.Column(db.Enum(MetricType), nullable=False, index=True)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=True)  # BRL, %, count, ms, etc.
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    frequency = db.Column(db.Enum(MetricFrequency), nullable=False)
    
    # Dimensões para segmentação
    affiliate_id = db.Column(db.String(50), nullable=True, index=True)
    user_id = db.Column(db.String(50), nullable=True, index=True)
    service_name = db.Column(db.String(50), nullable=True, index=True)
    region = db.Column(db.String(10), nullable=True, index=True)
    
    # Metadados adicionais
    meta_data = db.Column(db.Text, nullable=True)  # JSON string
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BusinessMetric {self.metric_name}: {self.value} {self.unit}>'
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_type': self.metric_type.value,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'frequency': self.frequency.value,
            'affiliate_id': self.affiliate_id,
            'user_id': self.user_id,
            'service_name': self.service_name,
            'region': self.region,
            'metadata': json.loads(self.meta_data) if self.meta_data else None,
            'created_at': self.created_at.isoformat()
        }

class AlertRule(db.Model):
    """Modelo para regras de alertas"""
    __tablename__ = 'alert_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), nullable=False, unique=True)
    metric_name = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(20), nullable=False)  # >, <, >=, <=, ==, !=
    threshold_value = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    
    # Configurações de notificação
    notification_channels = db.Column(db.Text, nullable=True)  # JSON: ["email", "slack", "webhook"]
    notification_recipients = db.Column(db.Text, nullable=True)  # JSON: ["email1", "email2"]
    
    # Estado da regra
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_triggered = db.Column(db.DateTime, nullable=True)
    trigger_count = db.Column(db.Integer, nullable=False, default=0)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AlertRule {self.rule_name}: {self.metric_name} {self.condition} {self.threshold_value}>'
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'metric_name': self.metric_name,
            'condition': self.condition,
            'threshold_value': self.threshold_value,
            'severity': self.severity,
            'notification_channels': json.loads(self.notification_channels) if self.notification_channels else [],
            'notification_recipients': json.loads(self.notification_recipients) if self.notification_recipients else [],
            'is_active': self.is_active,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'trigger_count': self.trigger_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AlertEvent(db.Model):
    """Modelo para eventos de alerta"""
    __tablename__ = 'alert_events'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_rule_id = db.Column(db.Integer, db.ForeignKey('alert_rules.id'), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    threshold_value = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    
    # Detalhes do evento
    message = db.Column(db.Text, nullable=False)
    context = db.Column(db.Text, nullable=True)  # JSON com contexto adicional
    
    # Estado do alerta
    status = db.Column(db.String(20), nullable=False, default='open')  # open, acknowledged, resolved
    acknowledged_by = db.Column(db.String(100), nullable=True)
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relacionamento
    alert_rule = db.relationship('AlertRule', backref=db.backref('events', lazy=True))
    
    def __repr__(self):
        return f'<AlertEvent {self.id}: {self.severity} - {self.status}>'
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'alert_rule_id': self.alert_rule_id,
            'rule_name': self.alert_rule.rule_name if self.alert_rule else None,
            'metric_value': self.metric_value,
            'threshold_value': self.threshold_value,
            'severity': self.severity,
            'message': self.message,
            'context': json.loads(self.context) if self.context else None,
            'status': self.status,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat()
        }

class ServiceHealth(db.Model):
    """Modelo para saúde dos serviços"""
    __tablename__ = 'service_health'
    
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(50), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)  # healthy, degraded, unhealthy
    response_time_ms = db.Column(db.Float, nullable=True)
    error_rate = db.Column(db.Float, nullable=True)  # 0-1
    cpu_usage = db.Column(db.Float, nullable=True)  # 0-1
    memory_usage = db.Column(db.Float, nullable=True)  # 0-1
    
    # Detalhes adicionais
    version = db.Column(db.String(20), nullable=True)
    uptime_seconds = db.Column(db.Integer, nullable=True)
    last_error = db.Column(db.Text, nullable=True)
    
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ServiceHealth {self.service_name}: {self.status}>'
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'service_name': self.service_name,
            'status': self.status,
            'response_time_ms': self.response_time_ms,
            'error_rate': self.error_rate,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'version': self.version,
            'uptime_seconds': self.uptime_seconds,
            'last_error': self.last_error,
            'timestamp': self.timestamp.isoformat()
        }

class DashboardConfig(db.Model):
    """Modelo para configuração de dashboards"""
    __tablename__ = 'dashboard_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    dashboard_name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Configuração do dashboard (JSON)
    config = db.Column(db.Text, nullable=False)  # JSON com widgets, layout, etc.
    
    # Permissões
    is_public = db.Column(db.Boolean, nullable=False, default=False)
    allowed_users = db.Column(db.Text, nullable=True)  # JSON array
    
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DashboardConfig {self.dashboard_name}>'
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'dashboard_name': self.dashboard_name,
            'description': self.description,
            'config': json.loads(self.config),
            'is_public': self.is_public,
            'allowed_users': json.loads(self.allowed_users) if self.allowed_users else [],
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

