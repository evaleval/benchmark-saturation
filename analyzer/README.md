The scripts for Team 3's (infrastructure) work.

A series of metrics, implemented in python, which transform an input csv of benchmark information (chiefly links to hf repos and downloads, other metadata) into additional csv rows in place.

"Metric" here is an abstraction that represents any *number* generated from a dataset. This can include live checks of citation counts, etc.

For now, we are implementing these metrics to be individually run manually, but we will eventually transition to an automated pipeline.