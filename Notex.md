To add a “summary statistics” object based on the time series data (reports and baseline), we can compute useful metrics such as:

🔢 Proposed Summary Stats:
	•	max_reports: peak report value and timestamp.
	•	average_reports: mean of all report values.
	•	max_deviation: biggest gap between reports and baseline.
	•	total_reports: sum of all report values.
	•	spikes: list of timestamps where reports exceed a threshold (e.g. 2× baseline).
	•	alerts_count: how many times baseline was exceeded significantly.