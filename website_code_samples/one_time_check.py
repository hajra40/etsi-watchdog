from etsi.watchdog import DriftCheck

check = DriftCheck(reference_df)
results = check.run(current_df, features=["age", "salary"])

for feature, result in results.items():
    print(result.summary())
    result.plot()
    result.to_json(f"logs/drift_{feature}.json")
