#!/usr/bin/env python3
"""
Rotas para sistema de monitoramento e métricas de negócio
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import json
import logging

from src.models.metrics import (
    db, BusinessMetric, AlertRule, AlertEvent, ServiceHealth, 
    DashboardConfig, MetricType, MetricFrequency
)

# Configuração de logging
logger = logging.getLogger(__name__)

# Blueprint para métricas
metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do serviço de monitoramento"""
    try:
        # Testa conexão com banco
        db.session.execute('SELECT 1')
        
        # Estatísticas básicas
        total_metrics = BusinessMetric.query.count()
        active_alerts = AlertRule.query.filter_by(is_active=True).count()
        recent_events = AlertEvent.query.filter(
            AlertEvent.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        return jsonify({
            'status': 'healthy',
            'service': 'monitoring-service',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'database': 'connected',
            'stats': {
                'total_metrics': total_metrics,
                'active_alerts': active_alerts,
                'recent_events_24h': recent_events
            }
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@metrics_bp.route('/metrics', methods=['POST'])
def record_metric():
    """Registra uma nova métrica de negócio"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['metric_name', 'metric_type', 'value', 'frequency']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Cria nova métrica
        metric = BusinessMetric(
            metric_name=data['metric_name'],
            metric_type=MetricType(data['metric_type']),
            value=float(data['value']),
            unit=data.get('unit'),
            frequency=MetricFrequency(data['frequency']),
            affiliate_id=data.get('affiliate_id'),
            user_id=data.get('user_id'),
            service_name=data.get('service_name'),
            region=data.get('region'),
            meta_data=json.dumps(data.get('metadata')) if data.get('metadata') else None,
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else datetime.utcnow()
        )
        
        db.session.add(metric)
        db.session.commit()
        
        # Verifica alertas
        check_alerts_for_metric(metric)
        
        return jsonify({
            'success': True,
            'metric_id': metric.id,
            'message': 'Metric recorded successfully'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid data: {e}'
        }), 400
    except Exception as e:
        logger.error(f"Error recording metric: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {e}'
        }), 500

@metrics_bp.route('/metrics/batch', methods=['POST'])
def record_metrics_batch():
    """Registra múltiplas métricas em lote"""
    try:
        data = request.get_json()
        
        if 'metrics' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing metrics array'
            }), 400
        
        if len(data['metrics']) > 1000:
            return jsonify({
                'success': False,
                'error': 'Batch size limit exceeded (max 1000 metrics)'
            }), 400
        
        metrics = []
        errors = []
        
        for i, metric_data in enumerate(data['metrics']):
            try:
                # Validação básica
                required_fields = ['metric_name', 'metric_type', 'value', 'frequency']
                for field in required_fields:
                    if field not in metric_data:
                        errors.append(f'Metric {i}: Missing field {field}')
                        continue
                
                # Cria métrica
                metric = BusinessMetric(
                    metric_name=metric_data['metric_name'],
                    metric_type=MetricType(metric_data['metric_type']),
                    value=float(metric_data['value']),
                    unit=metric_data.get('unit'),
                    frequency=MetricFrequency(metric_data['frequency']),
                    affiliate_id=metric_data.get('affiliate_id'),
                    user_id=metric_data.get('user_id'),
                    service_name=metric_data.get('service_name'),
                    region=metric_data.get('region'),
                    meta_data=json.dumps(metric_data.get('metadata')) if metric_data.get('metadata') else None,
                    timestamp=datetime.fromisoformat(metric_data['timestamp']) if metric_data.get('timestamp') else datetime.utcnow()
                )
                
                metrics.append(metric)
                
            except Exception as e:
                errors.append(f'Metric {i}: {str(e)}')
        
        if errors:
            return jsonify({
                'success': False,
                'errors': errors
            }), 400
        
        # Salva todas as métricas
        db.session.add_all(metrics)
        db.session.commit()
        
        # Verifica alertas para cada métrica
        for metric in metrics:
            check_alerts_for_metric(metric)
        
        return jsonify({
            'success': True,
            'metrics_recorded': len(metrics),
            'message': f'{len(metrics)} metrics recorded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error recording metrics batch: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {e}'
        }), 500

@metrics_bp.route('/metrics/query', methods=['GET'])
def query_metrics():
    """Consulta métricas com filtros"""
    try:
        # Parâmetros de consulta
        metric_name = request.args.get('metric_name')
        metric_type = request.args.get('metric_type')
        service_name = request.args.get('service_name')
        affiliate_id = request.args.get('affiliate_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 100))
        
        # Constrói query
        query = BusinessMetric.query
        
        if metric_name:
            query = query.filter(BusinessMetric.metric_name == metric_name)
        
        if metric_type:
            query = query.filter(BusinessMetric.metric_type == MetricType(metric_type))
        
        if service_name:
            query = query.filter(BusinessMetric.service_name == service_name)
        
        if affiliate_id:
            query = query.filter(BusinessMetric.affiliate_id == affiliate_id)
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(BusinessMetric.timestamp >= start_dt)
        
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(BusinessMetric.timestamp <= end_dt)
        
        # Ordena por timestamp desc e limita
        metrics = query.order_by(BusinessMetric.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [metric.to_dict() for metric in metrics],
            'count': len(metrics)
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid parameter: {e}'
        }), 400
    except Exception as e:
        logger.error(f"Error querying metrics: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {e}'
        }), 500

@metrics_bp.route('/metrics/aggregate', methods=['GET'])
def aggregate_metrics():
    """Agrega métricas por período"""
    try:
        # Parâmetros
        metric_name = request.args.get('metric_name', required=True)
        aggregation = request.args.get('aggregation', 'avg')  # sum, avg, min, max, count
        period = request.args.get('period', 'hour')  # hour, day, week, month
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Validação
        valid_aggregations = ['sum', 'avg', 'min', 'max', 'count']
        if aggregation not in valid_aggregations:
            return jsonify({
                'success': False,
                'error': f'Invalid aggregation. Must be one of: {valid_aggregations}'
            }), 400
        
        # Constrói query base
        query = db.session.query(BusinessMetric).filter(
            BusinessMetric.metric_name == metric_name
        )
        
        if start_date:
            query = query.filter(BusinessMetric.timestamp >= datetime.fromisoformat(start_date))
        
        if end_date:
            query = query.filter(BusinessMetric.timestamp <= datetime.fromisoformat(end_date))
        
        # Função de agregação
        if aggregation == 'sum':
            agg_func = func.sum(BusinessMetric.value)
        elif aggregation == 'avg':
            agg_func = func.avg(BusinessMetric.value)
        elif aggregation == 'min':
            agg_func = func.min(BusinessMetric.value)
        elif aggregation == 'max':
            agg_func = func.max(BusinessMetric.value)
        else:  # count
            agg_func = func.count(BusinessMetric.id)
        
        # Agrupamento por período
        if period == 'hour':
            time_group = func.strftime('%Y-%m-%d %H:00:00', BusinessMetric.timestamp)
        elif period == 'day':
            time_group = func.strftime('%Y-%m-%d', BusinessMetric.timestamp)
        elif period == 'week':
            time_group = func.strftime('%Y-W%W', BusinessMetric.timestamp)
        else:  # month
            time_group = func.strftime('%Y-%m', BusinessMetric.timestamp)
        
        # Executa agregação
        results = query.with_entities(
            time_group.label('period'),
            agg_func.label('value')
        ).group_by(time_group).order_by(time_group).all()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'period': result.period,
                    'value': float(result.value) if result.value else 0
                }
                for result in results
            ],
            'aggregation': aggregation,
            'period': period,
            'metric_name': metric_name
        })
        
    except Exception as e:
        logger.error(f"Error aggregating metrics: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {e}'
        }), 500

@metrics_bp.route('/alerts/rules', methods=['GET'])
def get_alert_rules():
    """Lista regras de alerta"""
    try:
        rules = AlertRule.query.all()
        
        return jsonify({
            'success': True,
            'data': [rule.to_dict() for rule in rules]
        })
        
    except Exception as e:
        logger.error(f"Error getting alert rules: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {e}'
        }), 500

@metrics_bp.route('/alerts/rules', methods=['POST'])
def create_alert_rule():
    """Cria nova regra de alerta"""
    try:
        data = request.get_json()
        
        # Validação
        required_fields = ['rule_name', 'metric_name', 'condition', 'threshold_value', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Cria regra
        rule = AlertRule(
            rule_name=data['rule_name'],
            metric_name=data['metric_name'],
            condition=data['condition'],
            threshold_value=float(data['threshold_value']),
            severity=data['severity'],
            notification_channels=json.dumps(data.get('notification_channels', [])),
            notification_recipients=json.dumps(data.get('notification_recipients', [])),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'rule_id': rule.id,
            'message': 'Alert rule created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {e}'
        }), 500

@metrics_bp.route('/alerts/events', methods=['GET'])
def get_alert_events():
    """Lista eventos de alerta"""
    try:
        # Parâmetros
        status = request.args.get('status')
        severity = request.args.get('severity')
        limit = int(request.args.get('limit', 50))
        
        # Query
        query = AlertEvent.query
        
        if status:
            query = query.filter(AlertEvent.status == status)
        
        if severity:
            query = query.filter(AlertEvent.severity == severity)
        
        events = query.order_by(AlertEvent.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [event.to_dict() for event in events]
        })
        
    except Exception as e:
        logger.error(f"Error getting alert events: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {e}'
        }), 500

@metrics_bp.route('/services/health', methods=['POST'])
def update_service_health():
    """Atualiza saúde de um serviço"""
    try:
        data = request.get_json()
        
        # Validação
        if 'service_name' not in data or 'status' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: service_name, status'
            }), 400
        
        # Cria registro de saúde
        health = ServiceHealth(
            service_name=data['service_name'],
            status=data['status'],
            response_time_ms=data.get('response_time_ms'),
            error_rate=data.get('error_rate'),
            cpu_usage=data.get('cpu_usage'),
            memory_usage=data.get('memory_usage'),
            version=data.get('version'),
            uptime_seconds=data.get('uptime_seconds'),
            last_error=data.get('last_error')
        )
        
        db.session.add(health)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Service health updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating service health: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {e}'
        }), 500

@metrics_bp.route('/services/health', methods=['GET'])
def get_services_health():
    """Obtém saúde atual dos serviços"""
    try:
        # Busca último status de cada serviço
        subquery = db.session.query(
            ServiceHealth.service_name,
            func.max(ServiceHealth.timestamp).label('max_timestamp')
        ).group_by(ServiceHealth.service_name).subquery()
        
        latest_health = db.session.query(ServiceHealth).join(
            subquery,
            and_(
                ServiceHealth.service_name == subquery.c.service_name,
                ServiceHealth.timestamp == subquery.c.max_timestamp
            )
        ).all()
        
        return jsonify({
            'success': True,
            'data': [health.to_dict() for health in latest_health]
        })
        
    except Exception as e:
        logger.error(f"Error getting services health: {e}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {e}'
        }), 500

def check_alerts_for_metric(metric):
    """Verifica se uma métrica dispara algum alerta"""
    try:
        # Busca regras ativas para esta métrica
        rules = AlertRule.query.filter(
            and_(
                AlertRule.metric_name == metric.metric_name,
                AlertRule.is_active == True
            )
        ).all()
        
        for rule in rules:
            # Avalia condição
            triggered = False
            
            if rule.condition == '>' and metric.value > rule.threshold_value:
                triggered = True
            elif rule.condition == '<' and metric.value < rule.threshold_value:
                triggered = True
            elif rule.condition == '>=' and metric.value >= rule.threshold_value:
                triggered = True
            elif rule.condition == '<=' and metric.value <= rule.threshold_value:
                triggered = True
            elif rule.condition == '==' and metric.value == rule.threshold_value:
                triggered = True
            elif rule.condition == '!=' and metric.value != rule.threshold_value:
                triggered = True
            
            if triggered:
                # Cria evento de alerta
                event = AlertEvent(
                    alert_rule_id=rule.id,
                    metric_value=metric.value,
                    threshold_value=rule.threshold_value,
                    severity=rule.severity,
                    message=f"Alert triggered: {metric.metric_name} = {metric.value} {metric.unit or ''} ({rule.condition} {rule.threshold_value})",
                    context=json.dumps({
                        'metric_id': metric.id,
                        'service_name': metric.service_name,
                        'affiliate_id': metric.affiliate_id,
                        'user_id': metric.user_id,
                        'timestamp': metric.timestamp.isoformat()
                    })
                )
                
                db.session.add(event)
                
                # Atualiza estatísticas da regra
                rule.last_triggered = datetime.utcnow()
                rule.trigger_count += 1
                
                logger.warning(f"Alert triggered: {rule.rule_name} - {event.message}")
        
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error checking alerts for metric {metric.id}: {e}")
        db.session.rollback()

