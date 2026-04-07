import os
import logging
import threading
import itertools
import time

logger = logging.getLogger("nuvox")

# On Render: set GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3 in the Environment Variables section of your Render service dashboard.

_all_keys = []

for key_name in ["GEMINI_API_KEY_1", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3", "GEMINI_API_KEY"]:
    val = os.getenv(key_name)
    if val and val.strip() and not val.startswith("PLACEHOLDER_"):
        # preserve order, prevent dupes just in case
        if val.strip() not in _all_keys:
            _all_keys.append(val.strip())

if not _all_keys:
    raise RuntimeError("[NUVOX] FATAL: No valid Gemini API keys found")

_key_cycle = itertools.cycle(_all_keys)
_key_lock = threading.Lock()
_cooling_keys = set()

logger.info(f"[NUVOX] Key rotation initialized — {len(_all_keys)} keys active")

def get_next_key() -> str:
    with _key_lock:
        if len(_cooling_keys) == len(_all_keys):
            # All keys are in cooldown
            logger.warning("[NUVOX] WARNING: All keys exhausted. Will retry in 30s")
            time.sleep(30)
            return _all_keys[0]

        for _ in range(len(_all_keys)):
            k = next(_key_cycle)
            if k not in _cooling_keys:
                return k
        
        # Fallback
        return _all_keys[0]

def _restore_key(key: str):
    with _key_lock:
        if key in _cooling_keys:
            _cooling_keys.remove(key)
            try:
                idx = _all_keys.index(key) + 1
            except ValueError:
                idx = "?"
            logger.info(f"[NUVOX] Key #{idx} restored from cooldown")

def mark_key_exhausted(key: str) -> None:
    with _key_lock:
        if key not in _cooling_keys:
            _cooling_keys.add(key)
            try:
                idx = _all_keys.index(key) + 1
            except ValueError:
                idx = "?"
            logger.warning(f"[NUVOX] Key #{idx} rate limited. Cooling down for 60s")
            
            if len(_cooling_keys) == len(_all_keys):
                logger.warning("[NUVOX] WARNING: All keys exhausted. Will retry in 30s")

            # Automatically restore after 60 seconds
            t = threading.Timer(60.0, _restore_key, args=[key])
            t.daemon = True
            t.start()

def get_key_status() -> dict:
    with _key_lock:
        return {
            "total": len(_all_keys),
            "active": len(_all_keys) - len(_cooling_keys),
            "cooling": len(_cooling_keys)
        }
