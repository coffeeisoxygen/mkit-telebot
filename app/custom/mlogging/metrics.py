# import json
# from collections import defaultdict

# from loguru import logger

# # TODO: Pindahkan ini ke config File , dan Integrasi dengan pydantic base class


# class MetricsCollector:
#     def __init__(self):
#         self.metrics = defaultdict(list)

#     def __call__(self, message):
#         """This method is called for every log message."""
#         record = message.record

#         # Only process METRIC level logs
#         if record["level"].name != "METRIC":
#             return

#         # Extract metric data from the 'extra' fields
#         extra = record["extra"]
#         if "metric_name" in extra and "value" in extra:
#             self.metrics[extra["metric_name"]].append({
#                 "value": extra["value"],
#                 "timestamp": record["time"].timestamp(),
#             })

#     def save_metrics(self):
#         """Save all collected metrics to a JSON file."""
#         with open("metrics.json", "w") as f:
#             json.dump(dict(self.metrics), f, indent=2)


# # Create the collector and add it as a sink
# collector = MetricsCollector()
# logger.add(collector)

# # Create the METRIC level
# logger.level("METRIC", no=38)

# # Now when you log metrics, they're automatically collected
# # The bind() method attaches extra data to the log entry
# logger.bind(metric_name="response_time", value=0.234).log("METRIC", "API response")
# logger.bind(metric_name="response_time", value=0.189).log("METRIC", "API response")
# logger.bind(metric_name="active_users", value=1523).log("METRIC", "User count")

# # Later, save all metrics to file
# collector.save_metrics()

# # The metrics.json file will contain:
# # {
# #   "response_time": [
# #     {"value": 0.234, "timestamp": 1627...},
# #     {"value": 0.189, "timestamp": 1627...}
# #   ],
# #   "active_users": [
# #     {"value": 1523, "timestamp": 1627...}
# #   ]
# # }
