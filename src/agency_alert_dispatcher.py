from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from .config import load_settings
from .agency_registry import AgencyRegistry
from .alert_policy import evaluate_agency_alert
from .map_link_provider import generate_map_link
from .notifications import MockSMSChannel, SIM7600SMSChannel, WebhookChannel, EmailChannel


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')


class AgencyAlertDispatcher:
    def __init__(self, database, registry: AgencyRegistry | None = None, channels: dict[str, Any] | None = None):
        self.db = database
        self.registry = registry or AgencyRegistry()
        cfg = load_settings()
        acfg = cfg.get('agency_alerts', {})
        self.mode = str(acfg.get('dispatch_mode','DEMO')).upper()
        self.production = bool(acfg.get('production_mode', False))
        simcfg = cfg.get('sim7600', {})
        default_sms = SIM7600SMSChannel(simcfg.get('serial_port','/dev/ttyUSB2'), simcfg.get('baudrate',115200), simcfg.get('timeout_seconds',8)) if self.production else MockSMSChannel(True)
        self.channels = channels or {'sms': default_sms, 'webhook': WebhookChannel(), 'email': EmailChannel()}

    def format_message(self, result: dict[str, Any]) -> str:
        e = result.get('evidence', {})
        loc = result.get('location') or {}
        c = loc.get('centroid') or {}
        map_link = ''
        if c.get('latitude') is not None and c.get('longitude') is not None:
            map_link = generate_map_link(c['latitude'], c['longitude'])
        area = result.get('suspected_zone','UNKNOWN').replace('_',' ')
        return (
            'GOLDTRACE CRITICAL ALERT\n'
            'Suspected mining/galamsey activity detected.\n'
            f"Event: {result.get('event_id')}\n"
            f"Risk: {result.get('risk_level')}\n"
            f"Confidence: {100*float(result.get('confidence',0)):.0f}%\n"
            f"Area: {area}\n"
            f"River Segment: {loc.get('segment_id') or 'N/A'}\n"
            f"Approx Location: {c.get('latitude','N/A')}, {c.get('longitude','N/A')}\n"
            f"District: {loc.get('district','N/A')}\n"
            f"Turbidity change: {float(e.get('turbidity_difference',0)):+.1f} NTU\n"
            f"Machine audio: {100*float(e.get('audio_machine_probability',0)):.0f}%\n"
            f"Heavy vibration: {100*float(e.get('vibration_machinery_probability',0)):.0f}%\n"
            f"Duration: {float(e.get('persistence_seconds',0)):.0f} sec\n"
            + (f"Map: {map_link}\n" if map_link else '') +
            'Action: Investigate suspected river section.'
        )

    def dispatch(self, result: dict[str, Any], force: bool = False) -> dict[str, Any]:
        policy = evaluate_agency_alert(result)
        if not force and not policy.get('eligible'):
            return {**policy, 'dispatch_status':'NOT_ELIGIBLE', 'deliveries':[]}
        if self.mode == 'OFF':
            return {**policy, 'dispatch_status':'OFF', 'deliveries':[]}
        if self.mode == 'MANUAL' and not force:
            return {**policy, 'dispatch_status':'AWAITING_MANUAL_APPROVAL', 'deliveries':[]}

        event_id = result.get('event_id')
        if event_id and self.db.has_recent_agency_dispatch(event_id, result.get('risk_level','UNKNOWN')) and not force:
            return {**policy, 'dispatch_status':'DEDUPLICATED', 'deliveries':[]}

        recipients = self.registry.list(True)
        message = self.format_message(result)
        deliveries = []
        for agency in recipients:
            for channel_name, enabled in (agency.get('channels') or {}).items():
                if not enabled or channel_name not in self.channels:
                    continue
                destination = agency.get({'sms':'phone','webhook':'webhook_url','email':'email'}.get(channel_name,''))
                if not destination:
                    continue
                # Placeholders are acceptable in DEMO but must never be used as production destinations.
                if self.production and ('X' in str(destination) or 'example' in str(destination).lower()):
                    continue
                delivery_id = self.db.create_alert_delivery(event_id, agency.get('id'), channel_name, str(destination), 'PENDING')
                channel = self.channels[channel_name]
                result_send = channel.send(str(destination), message)
                status = result_send.status if result_send.success else 'FAILED'
                self.db.update_alert_delivery(delivery_id, status, result_send.provider_response, result_send.error)
                if not result_send.success:
                    self.db.enqueue_alert(event_id, agency.get('id'), channel_name, str(destination), message, result.get('location'))
                deliveries.append({'delivery_id':delivery_id,'agency_id':agency.get('id'),'channel':channel_name,'destination':destination,'status':status,'error':result_send.error})

        dispatch_status = 'SIMULATED' if not self.production or self.mode == 'DEMO' else ('SENT' if any(d['status']=='SENT' for d in deliveries) else 'QUEUED')
        self.db.record_agency_dispatch(event_id, result.get('risk_level','UNKNOWN'), dispatch_status, {'policy':policy,'deliveries':deliveries,'message':message,'timestamp':_now()})
        return {**policy, 'dispatch_status':dispatch_status, 'deliveries':deliveries, 'message':message, 'recipient_count':len(recipients)}

    def retry_queue(self) -> dict[str, int]:
        cfg = load_settings().get('agency_alerts', {})
        max_retries = int(cfg.get('max_retries', 3))
        attempted = sent = failed = 0
        for item in self.db.pending_alert_queue():
            if int(item.get('attempt_count',0)) >= max_retries:
                self.db.mark_queue_exhausted(item['queue_id']); continue
            channel = self.channels.get(item['channel'])
            if channel is None: continue
            attempted += 1
            r = channel.send(item['destination'], item['message'])
            self.db.update_queue_attempt(item['queue_id'], r.success, r.error)
            if r.success: sent += 1
            else: failed += 1
        return {'attempted':attempted,'sent':sent,'failed':failed}
