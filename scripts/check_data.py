from sdg.open_sdg import open_sdg_check
from alter_data import alter_data

validation_successful = open_sdg_check(
    config='config_data.yml',
    alter_data=alter_data,
)
# Validate the indicators.
# validation_successful = open_sdg_check(config='config_data.yml')

# If everything was valid, perform the build.
if not validation_successful:
    raise Exception('There were validation errors. See output above.')
