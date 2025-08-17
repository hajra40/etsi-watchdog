from etsi.watchdog import DriftComparator

comp = DriftComparator(run1_results, run2_results)
diff = comp.diff()

for feature, delta in diff.items():
    print(f"{feature}: Δ PSI = {delta:+.4f}")