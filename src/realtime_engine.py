from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from .sensor_validator import validate_packet
from .synchronization import synchronize_packets
from .feature_engineering import node_comparison_features
from .confidence_engine import calculate_confidence
from .risk_engine import assess_risk
from .persistence_tracker import PersistenceTracker
from .event_tracker import EventTracker
from .localization import estimate_zone
from .database import Database
from .model_manager import ModelManager
from .alert_manager import AlertManager
from .geospatial import GeospatialEngine
from .agency_alert_dispatcher import AgencyAlertDispatcher


class RealtimeEngine:
    def __init__(self, models: ModelManager | None = None, database: Database | None = None):
        self.models = models or ModelManager()
        self.db = database or Database()
        self.events = EventTracker()
        self.alerts = AlertManager()
        self.geospatial = GeospatialEngine()
        self.agency_dispatcher = AgencyAlertDispatcher(self.db)
        self.persistence = PersistenceTracker()

    @staticmethod
    def _utc() -> str:
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def _uncertain(self, a: dict[str, Any], b: dict[str, Any], va: dict, vb: dict, sync: dict) -> dict:
        result = {
            'event_id': None,
            'timestamp': self._utc(),
            'prediction': 'SYSTEM_UNCERTAIN',
            'human_description': 'Insufficient reliable sensor evidence',
            'risk_level': 'UNKNOWN',
            'confidence': 0.2,
            'suspected_zone': 'NO_SUSPECTED_ZONE',
            'location': None,
            'map': None,
            'node_results': {
                'NODE_A': {'environment':'UNKNOWN_ENVIRONMENTAL_CHANGE','audio':'UNKNOWN_AUDIO','vibration':'UNKNOWN_VIBRATION','health':va['health'],'turbidity_ntu':a.get('turbidity_ntu')},
                'NODE_B': {'environment':'UNKNOWN_ENVIRONMENTAL_CHANGE','audio':'UNKNOWN_AUDIO','vibration':'UNKNOWN_VIBRATION','health':vb['health'],'turbidity_ntu':b.get('turbidity_ntu')},
            },
            'evidence': {'sync_delta_seconds':sync['delta_seconds'],'validation_issues':{'NODE_A':va['issues'],'NODE_B':vb['issues']},'persistence_seconds':0.0},
            'top_factors': [],
            'agency_alert': {'eligible':False,'dispatch_status':'NOT_ELIGIBLE','reason':'SYSTEM_UNCERTAIN'},
            'recommendation': 'Check sensor health and communication before interpreting the event.',
        }
        self.db.save_prediction(result)
        return result

    def process_pair(self, a: dict[str, Any], b: dict[str, Any], persistence_seconds: float | None = None) -> dict:
        self.db.save_sensor_reading(a); self.db.save_sensor_reading(b)
        va = validate_packet(a); vb = validate_packet(b); sync = synchronize_packets(a, b)
        if not sync['synchronized'] or va['health'] == 'FAILED' or vb['health'] == 'FAILED':
            self.persistence.reset()

            return self._uncertain(a, b, va, vb, sync)

        auto_persistence = (
            persistence_seconds is None
        )

        effective_persistence = (
            0.0
            if auto_persistence
            else max(
                0.0,
                float(persistence_seconds),
            )
        )

        audio_a = self.models.audio.predict(a['audio_samples'], a['audio_sample_rate'])
        audio_b = self.models.audio.predict(b['audio_samples'], b['audio_sample_rate'])
        vib_a = self.models.vibration.predict(a['vibration_samples'], a['vibration_sample_rate'])
        vib_b = self.models.vibration.predict(b['vibration_samples'], b['vibration_sample_rate'])

        fa = {**a, **audio_a['features'], **vib_a['features'], 'audio_machine_probability':audio_a['machine_probability'], 'vibration_machinery_probability':vib_a['machinery_probability']}
        fb = {**b, **audio_b['features'], **vib_b['features'], 'audio_machine_probability':audio_b['machine_probability'], 'vibration_machinery_probability':vib_b['machinery_probability']}
        comp = node_comparison_features(fa, fb)
        comp.update({
            'turbidity_a':a['turbidity_ntu'], 'turbidity_b':b['turbidity_ntu'],
            'audio_machine_probability_a':audio_a['machine_probability'], 'audio_machine_probability_b':audio_b['machine_probability'],
            'vibration_machinery_probability_a':vib_a['machinery_probability'], 'vibration_machinery_probability_b':vib_b['machinery_probability'],
            'persistence_seconds':effective_persistence,
        })

        env = self.models.environment.predict(comp)
        anomaly = self.models.anomaly.predict(comp); comp.update(anomaly)
        fusion = self.models.fusion.predict(comp)
        turbidity_strength = min(1.0, abs(float(comp.get('turbidity_difference',0))) / 50.0)
        confidence = calculate_confidence(fusion['confidence'], audio_b['confidence'], vib_b['confidence'], env['confidence'], [va['health'], vb['health']], sync['quality'], anomaly.get('anomaly_score',0), 1.0, [audio_b['machine_probability'], vib_b['machinery_probability'], turbidity_strength])

        risk = assess_risk(
            fusion['class'],
            confidence,
            comp,
            [va['health'], vb['health']],
        )

        if auto_persistence:
            critical_candidate = bool(
                risk.get(
                    'critical_candidate',
                    False,
                )
            )

            effective_persistence = (
                self.persistence.update(
                    critical_candidate
                )
            )

            if effective_persistence > 0.0:
                comp[
                    'persistence_seconds'
                ] = effective_persistence

                env = (
                    self.models.environment.predict(
                        comp
                    )
                )

                anomaly = (
                    self.models.anomaly.predict(
                        comp
                    )
                )

                comp.update(
                    anomaly
                )

                fusion = (
                    self.models.fusion.predict(
                        comp
                    )
                )

                turbidity_strength = min(
                    1.0,
                    abs(
                        float(
                            comp.get(
                                'turbidity_difference',
                                0,
                            )
                        )
                    ) / 50.0,
                )

                confidence = calculate_confidence(
                    fusion['confidence'],
                    audio_b['confidence'],
                    vib_b['confidence'],
                    env['confidence'],
                    [
                        va['health'],
                        vb['health'],
                    ],
                    sync['quality'],
                    anomaly.get(
                        'anomaly_score',
                        0,
                    ),
                    1.0,
                    [
                        audio_b[
                            'machine_probability'
                        ],
                        vib_b[
                            'machinery_probability'
                        ],
                        turbidity_strength,
                    ],
                )

                risk = assess_risk(
                    fusion['class'],
                    confidence,
                    comp,
                    [
                        va['health'],
                        vb['health'],
                    ],
                )
        else:
            self.persistence.reset()

        a_abnormal = a['turbidity_ntu'] > 40 or audio_a['machine_probability'] > .65 or vib_a['machinery_probability'] > .65
        b_abnormal = b['turbidity_ntu'] > 40 or audio_b['machine_probability'] > .65 or vib_b['machinery_probability'] > .65
        zone = estimate_zone(a_abnormal, b_abnormal)
        involved = ['NODE_A','NODE_B'] if b_abnormal else (['NODE_A'] if a_abnormal else [])
        ev = self.events.update(risk['prediction'], risk['risk_level'], confidence, involved)

        evidence = {
            'turbidity_difference': comp['turbidity_difference'],
            'audio_machine_probability': audio_b['machine_probability'],
            'vibration_machinery_probability': vib_b['machinery_probability'],
            'persistent_activity': bool(risk.get('persistence_met', False)),
            'persistence_seconds': float(effective_persistence),
            'required_persistence_seconds': float(risk.get('required_persistence_seconds', 0.0)),
            'multi_sensor_confirmation': comp['multi_sensor_confirmation_score'] >= .66,
            'multi_sensor_confirmation_score': comp['multi_sensor_confirmation_score'],
            'anomaly_score': anomaly.get('anomaly_score',0),
            'reasons': risk['reasons'],
        }
        factors = sorted([
            {'feature':'turbidity_difference','value':comp['turbidity_difference'],'importance':'HIGH' if abs(comp['turbidity_difference'])>25 else 'MEDIUM'},
            {'feature':'audio_machine_probability','value':audio_b['machine_probability'],'importance':'HIGH' if audio_b['machine_probability']>.7 else 'MEDIUM'},
            {'feature':'vibration_machinery_probability','value':vib_b['machinery_probability'],'importance':'HIGH' if vib_b['machinery_probability']>.7 else 'MEDIUM'},
        ], key=lambda x: abs(float(x['value'])), reverse=True)

        location = self.geospatial.resolve(zone, ev.get('event_id'), risk['risk_level'])
        result = {
            'event_id':ev.get('event_id'),
            'timestamp':self._utc(),
            'prediction':risk['prediction'],
            'human_description':'Suspected galamsey/mining activity requiring investigation' if risk['risk_level']=='CRITICAL' else risk['prediction'].replace('_',' ').title(),
            'risk_level':risk['risk_level'],
            'confidence':confidence,
            'suspected_zone':zone,
            'location':location,
            'node_results':{
                'NODE_A':{'environment':'NORMAL_RIVER' if not a_abnormal else 'UNKNOWN_ENVIRONMENTAL_CHANGE','audio':audio_a['audio_class'],'vibration':vib_a['vibration_class'],'audio_machine_probability':audio_a['machine_probability'],'vibration_machinery_probability':vib_a['machinery_probability'],'health':va['health'],'turbidity_ntu':a['turbidity_ntu']},
                'NODE_B':{'environment':env['environment_class'],'audio':audio_b['audio_class'],'vibration':vib_b['vibration_class'],'audio_machine_probability':audio_b['machine_probability'],'vibration_machinery_probability':vib_b['machinery_probability'],'health':vb['health'],'turbidity_ntu':b['turbidity_ntu']},
            },
            'evidence':evidence,
            'top_factors':factors,
            'recommendation':'Security/environmental authorities should investigate the monitored river section between Node A and Node B.' if risk['risk_level']=='CRITICAL' and location else ('Investigate the river section between Node A and Node B.' if risk['risk_level']=='HIGH' else 'Continue monitoring and correlate with additional evidence.'),
        }
        result.update(self.geospatial.map_payload(result))

        # Local alert record.
        if self.alerts.should_alert(result.get('event_id'), result.get('risk_level','UNKNOWN')):
            message = self.alerts.format_alert(result); result['alert_generated']=True; result['alert_message']=message; result['alert_id']=self.db.save_alert(result,message)
        else:
            result['alert_generated']=False

        # External agency dispatch (DEMO by default; real sends require explicit production config).
        result['agency_alert'] = self.agency_dispatcher.dispatch(result)
        self.db.save_prediction(result)
        return result

