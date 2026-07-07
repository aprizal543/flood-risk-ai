"""startup.py – Application warm-up and eager loading orchestration.

Moves all lazy-loaded ML asset initialisation from first-request critical
path to application startup so that the first user request completes at
steady-state speed (~29 ms) instead of ~1528 ms.
"""

from __future__ import annotations

import logging
import time

logger = logging.getLogger(__name__)


class AppStartup:
    """Orchestrates eager loading of ML assets and warm-up prediction.

    Usage:
        startup = AppStartup()
        startup.warm_up()
        ready = startup.is_ready
    """

    def __init__(self) -> None:
        self._ready: bool = False
        self._elapsed_ms: float = 0.0

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def elapsed_ms(self) -> float:
        return self._elapsed_ms

    def warm_up(self) -> None:
        """Execute warm-up sequence: imports, model loading, warm-up predict.

        Raises:
            Exception: Re-raises any error from loading or prediction so that
                       FastAPI startup event fails loudly (fail-fast).
        """
        start = time.perf_counter()

        # 1. Eager sklearn import (normally lazy-loaded by joblib unpickling)
        import sklearn.ensemble._forest  # noqa: F401

        # 2. Load Random Forest model
        from ml.predict.random_forest import _load_model
        _load_model()

        # 3. Load feature list & scaler
        from ml.predict.preprocess import get_feature_list, get_scaler
        get_feature_list()
        get_scaler()

        # 4. Load commodity profiles (independently cached by scorer & explain)
        from ml.recommendation.scorer import _load_profiles as _load_scorer_profiles
        from ml.recommendation.explain import _load_profiles as _load_explain_profiles
        _load_scorer_profiles()
        _load_explain_profiles()

        # 5. Load mitigation rules
        from ml.recommendation.mitigation import _load_rules
        _load_rules()

        # 6. Warm-up prediction – cold-run through the full RF pipeline
        from ml.predict.preprocess import get_feature_list, prepare_dataframe
        from ml.predict.random_forest import predict_rf
        features = get_feature_list()
        dummy = {f: 0.0 for f in features}
        df = prepare_dataframe(dummy)
        predict_rf(df)

        self._elapsed_ms = (time.perf_counter() - start) * 1000
        self._ready = True
        logger.info("Warm-up complete in %.0f ms", self._elapsed_ms)
