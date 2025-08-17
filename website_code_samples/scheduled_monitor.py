from etsi.watchdog import Monitor

monitor = Monitor(reference_df)
monitor.enable_logging("logs/rolling_log.csv")

monitor.watch_rolling(
    df=live_df,
    window=50,
    freq="D",
    features=["age", "salary"]
)