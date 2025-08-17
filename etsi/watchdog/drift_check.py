# etsi/watchdog/drift_check.py

from .drift.factory import get_drift_function
from .drift.base import DriftResult
from etsi.watchdog.reports import generate_drift_pdf

class DriftCheck:
    """
    DriftCheck — Core API to detect drift between reference and current datasets.

    Example:
    >>> check = DriftCheck(reference_df)
    >>> results = check.run(current_df, features=["age", "salary"])
    """

    def __init__(self, reference_df, algorithm="psi", threshold=0.2):
        self.reference = reference_df
        self.algorithm = algorithm
        self.threshold = threshold
        self._func = get_drift_function(algorithm)

    # etsi/watchdog/drift_check.py

    def run(self, current_df, features, pdf_report=None):
    # """
    # Run drift detection on a set of features.

    # Parameters
    # ----------
    # current_df : pandas.DataFrame
    #     The current dataset to evaluate.
    # features : list of str
    #     List of feature names to check for drift.
    # pdf_report : str, optional
    #     If provided, saves a PDF drift summary report to this path.

    # Returns
    # -------
    # dict
    #     Mapping of feature name -> DriftResult object.
    # """
        results = {}
        for feat in features:
            if feat not in self.reference.columns or feat not in current_df.columns:
                print(f"[etsi-watchdog] Skipping '{feat}' — missing in one of the datasets.")
                continue

            result = self._func(
                reference_df=self.reference,
                current_df=current_df,
                feature=feat,
                threshold=self.threshold
            )

            if result is not None:
                results[feat] = result
            
            if pdf_report:
                try:
                    #from .reports import generate_drift_pdf
                    generate_drift_pdf(results, pdf_report)
                    print(f"[etsi-watchdog] PDF drift summary saved to {pdf_report}")
                except ImportError:
                    print("[etsi-watchdog] PDF generation skipped — 'reports.py' not found.")
                except Exception as e:
                    print(f"[etsi-watchdog] Error generating PDF: {e}")
        return results
