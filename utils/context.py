import os
import yaml
import uuid

# out-of-the-box configs parameters
default_params = ['TRACKING_ID']
main_dir = os.path.dirname(__file__)
context = {}

# reading the application schema
with open(os.path.join(main_dir, "../config", "config.yaml"), "r") as ymlfile:
    app_config = yaml.full_load(ymlfile)

# reading the test config
with open(os.path.join(main_dir, "../config", "config-test.yaml"), "r") as ymlfile:
    test_config = yaml.full_load(ymlfile)

# get the values from the default values in the schema and override with env variable values if available
for key in app_config['application']['schema']:
    context[key['name']] = key['defaultValue']

# updating the context with the test_config to override the default values
if test_config is not None:
    context.update(test_config)

# override all with env variables
for key in app_config['application']['schema']:
    if os.environ.get(key['name']) is not None:
        context[key['name']] = os.environ.get(key['name'])

# load pre-defined env variables
for key in default_params:
    context[key] = os.environ.get(key)

#  generate TRACKING_ID if not provided externally
if context['TRACKING_ID'] is None:
    context['TRACKING_ID'] = str(uuid.uuid4())


