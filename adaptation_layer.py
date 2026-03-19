# adaptation_layer.py
import time
from copy import deepcopy
from typing import Dict, Any, Optional, Callable, TYPE_CHECKING

TelemetryHook = Callable[[str, Dict[str, Any]], None]

if TYPE_CHECKING:
    from engine import EMSEngine, EthicalMemory



class AdaptationLayer:
    """
    ADL — Adaptation Layer (Engine‑Integrated)

    This version is aligned with your actual EMSEngine:
    - Uses drift from engine.value_drift
    - Uses tension_index from EthicalMemory
    - Adjusts modify_threshold and block_threshold
    - Adjusts CEL multipliers (ContextualEthicsLayer.mods)
    - Respects safety floors and max shift limits
    """

    def __init__(self, telemetry_hook: Optional[TelemetryHook] = None):
        self._telemetry_hook = telemetry_hook
        self._last_ts = 0.0

    # ----------------------------------------------------------------------
    # Telemetry
    # ----------------------------------------------------------------------

    def _emit(self, event: str, data: Dict[str, Any]) -> None:
        """
        Emit a telemetry event if a hook is registered.
        """
        if self._telemetry_hook:
            self._telemetry_hook(event, data)

    # ----------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------

    def adapt(
        self,
        engine: "EMSEngine",
        memory: "EthicalMemory",
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Adapt engine parameters based on:
        - drift (engine.value_drift)
        - tension (memory.tension_index)

        Returns a *new* config dict (deep copy).
        """

        adapt_cfg = config.get("adaptation", {})
        if not adapt_cfg.get("enabled", False):
            return config

        cooldown = adapt_cfg.get("cooldown_seconds", 300)
        now = time.time()

        if now - self._last_ts < cooldown:
            return config

        new_cfg = deepcopy(config)
        deltas = {}

        # Compute drift magnitude
        drift_value = self._compute_drift(engine)

        # Apply threshold adaptation
        t_delta = self._adapt_thresholds(new_cfg, drift_value, adapt_cfg)
        if t_delta:
            deltas["thresholds"] = t_delta

        # Apply CEL multiplier adaptation
        c_delta = self._adapt_cel(engine, new_cfg, memory.tension_index, adapt_cfg)
        if c_delta:
            deltas["cel_multipliers"] = c_delta

        if not deltas:
            return config

        self._last_ts = now
        self._emit("adaptation_applied", {
            "deltas": deltas,
            "drift": drift_value,
            "tension": memory.tension_index,
        })

        return new_cfg

    # ----------------------------------------------------------------------
    # Drift computation
    # ----------------------------------------------------------------------

    def _compute_drift(self, engine: "EMSEngine") -> float:
        """
        Compute drift as the mean absolute deviation across CVL tags.
        """
        values = []
        for tag, history in engine.value_drift.items():
            if history:
                values.append(abs(sum(history) / len(history)))

        if not values:
            return 0.0

        return round(sum(values) / len(values), 3)

    # ----------------------------------------------------------------------
    # Threshold adaptation
    # ----------------------------------------------------------------------

    def _adapt_thresholds(
        self,
        cfg: Dict[str, Any],
        drift: float,
        adapt_cfg: Dict[str, Any],
    ) -> Optional[Dict[str, float]]:

        max_shift = adapt_cfg.get("max_threshold_shift", 0.02)
        min_block = adapt_cfg.get("min_block_threshold", 0.5)

        modify = cfg.get("modify_threshold")
        block = cfg.get("block_threshold_nominal")

        if modify is None or block is None:
            return None

        delta = 0.0

        if drift > 0.15:
            delta = +max_shift
        elif drift < 0.05:
            delta = -max_shift

        if delta == 0.0:
            return None

        new_modify = modify + delta
        new_block = block + delta

        # Safety floors
        if new_block < min_block:
            new_block = min_block
        if new_modify >= new_block:
            new_modify = new_block - 0.01

        cfg["modify_threshold"] = new_modify
        cfg["block_threshold_nominal"] = new_block

        return {"modify_threshold": new_modify, "block_threshold_nominal": new_block}

        # ----------------------------------------------------------------------
    # CEL multiplier adaptation
    # ----------------------------------------------------------------------

    def _adapt_cel(
        self,
        engine: "EMSEngine",
        cfg: Dict[str, Any],
        tension: float,
        adapt_cfg: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Adjust CEL multipliers based on tension index and drift.
        """
        cel_cfg = cfg.get("cel", {})
        if not cel_cfg:
            return None

        drift = self._compute_drift(engine)

        # Base multiplier adjustments
        mods = {
            "HIGH_RISK": 1.0,
            "RESEARCH": 1.0,
            "LOW_RISK": 1.0,
        }

        # Tension-based adjustments
        if tension > 0.7:
            mods["HIGH_RISK"] += 0.5
            mods["RESEARCH"] += 0.3
        elif tension < 0.3:
            mods["HIGH_RISK"] -= 0.3
            mods["RESEARCH"] -= 0.2

        # Drift-based adjustments
        if drift > 0.15:
            mods["HIGH_RISK"] += 0.2
        elif drift < 0.05:
            mods["HIGH_RISK"] -= 0.1

        # Safety floors
        for key in mods:
            if mods[key] < 0.5:
                mods[key] = 0.5

        cel_cfg["mods"] = mods
        return {"cel_mods": mods}
