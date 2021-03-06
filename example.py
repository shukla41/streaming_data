from __future__ import absolute_import

import logging
import argparse
import apache_beam as beam

'''Normalize pubsub string to json object'''
# Lines look like this:
def parse_pubsub(line):
    schema_cols = ["ride_id",
                   "point_idx",
                   "latitude",
                   "longitude",
                   "timestamp",
                   "meter_reading",
                   "meter_increment",
                   "ride_status",
                   "passenger_count"]
    import json
    record = json.loads(line)
    return {s: record['{}'.format(s)] for s in schema_cols}
    # return (record['vendor_id']), (record['pickup_datetime']), (record['dropoff_datetime'])

def run(argv=None):
  """Build and run the pipeline."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input_topic', required=True,
      help='Input PubSub topic of the form "/topics/<PROJECT>/<TOPIC>".')
  parser.add_argument(
      '--output_table', required=True,
      help=
      ('Output BigQuery table for results specified as: PROJECT:DATASET.TABLE '
       'or DATASET.TABLE.'))
  known_args, pipeline_args = parser.parse_known_args(argv)

  with beam.Pipeline(argv=pipeline_args) as p:
    # Read the pubsub topic into a PCollection.
    lines = ( p | beam.io.ReadStringsFromPubSub(known_args.input_topic)
                | beam.Map(parse_pubsub)
                | beam.io.WriteToBigQuery(
                    known_args.output_table,
                    schema='''
                    ride_id:STRING,
                    point_idx:INTEGER,
                    latitude:FLOAT,
                    longitude:FLOAT,
                    timestamp:TIMESTAMP,
                    meter_reading:FLOAT,
                    meter_increment:FLOAT,
                    ride_status:STRING,
                    passenger_count:INTEGER
                    ''',
                    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                    write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
            )

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
