# category_predictor/predictor_singleton.py

from .category_predictor import CategoryPredictor

_predictor = None

def get_predictor():
    """
    Returns a singleton instance of CategoryPredictor.
    Loads the model only once during the entire application run.
    """
    global _predictor
    if _predictor is None:
        _predictor = CategoryPredictor()  # expensive load happens ONCE
    return _predictor
