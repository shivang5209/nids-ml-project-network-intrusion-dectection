from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Event, Lock, Thread
from typing import Any

from app.db.session import SessionLocal
from app.schemas.predict import PredictRequest
from app.services.prediction_pipeline import persist_prediction


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CaptureState:
    running: bool = False
    interface: str | None = None
    interval_seconds: int = 5
    batches_processed: int = 0
    last_batch_at: str | None = None
    last_error: str | None = None
    last_feature_snapshot: dict[str, Any] | None = None


class LiveCaptureManager:
    def __init__(self) -> None:
        self._lock = Lock()
        self._stop_event = Event()
        self._thread: Thread | None = None
        self._state = CaptureState()

    def start(self, interface: str | None = None, interval_seconds: int = 5) -> CaptureState:
        with self._lock:
            if self._state.running:
                return self._state

            self._state.running = True
            self._state.interface = interface
            self._state.interval_seconds = max(1, int(interval_seconds))
            self._state.last_error = None
            self._stop_event.clear()
            self._thread = Thread(target=self._capture_loop, daemon=True)
            self._thread.start()
            return self._state

    def stop(self) -> CaptureState:
        with self._lock:
            if not self._state.running:
                return self._state
            self._stop_event.set()
            thread = self._thread

        if thread is not None:
            thread.join(timeout=3)

        with self._lock:
            self._state.running = False
            self._thread = None
            return self._state

    def status(self) -> CaptureState:
        with self._lock:
            return self._state

    def _capture_loop(self) -> None:
        try:
            from scapy.all import IP, sniff  # type: ignore
        except Exception as exc:  # pragma: no cover
            with self._lock:
                self._state.running = False
                self._state.last_error = f"Scapy unavailable: {exc}"
            return

        while not self._stop_event.is_set():
            try:
                with self._lock:
                    interval = self._state.interval_seconds
                    interface = self._state.interface

                packets = sniff(timeout=interval, store=True, iface=interface, filter="ip")
                features = self._build_features(packets, interval, IP)
                if features is None:
                    continue

                payload = PredictRequest(**features)
                with SessionLocal() as db:
                    persist_prediction(payload, db)

                with self._lock:
                    self._state.batches_processed += 1
                    self._state.last_batch_at = _now_iso()
                    self._state.last_feature_snapshot = features
            except Exception as exc:  # pragma: no cover
                with self._lock:
                    self._state.last_error = str(exc)

        with self._lock:
            self._state.running = False

    @staticmethod
    def _build_features(packets: list[Any], interval: int, ip_layer: Any) -> dict[str, Any] | None:
        if not packets:
            return None

        flow_counter: Counter[tuple[str, str, str]] = Counter()
        total_bytes = 0
        packet_count = 0

        for packet in packets:
            if not packet.haslayer(ip_layer):
                continue

            ip_part = packet[ip_layer]
            protocol_number = int(getattr(ip_part, "proto", 0))
            protocol_name = {1: "ICMP", 6: "TCP", 17: "UDP"}.get(protocol_number, "TCP")
            source_ip = str(getattr(ip_part, "src", "0.0.0.0"))
            destination_ip = str(getattr(ip_part, "dst", "0.0.0.0"))

            flow_counter[(source_ip, destination_ip, protocol_name)] += 1
            packet_count += 1
            total_bytes += len(packet)

        if not flow_counter or packet_count == 0:
            return None

        (source_ip, destination_ip, protocol), _ = flow_counter.most_common(1)[0]
        return {
            "source_ip": source_ip,
            "destination_ip": destination_ip,
            "protocol": protocol,
            "packet_count": packet_count,
            "byte_count": total_bytes,
            "flow_duration": float(interval),
        }


live_capture_manager = LiveCaptureManager()
