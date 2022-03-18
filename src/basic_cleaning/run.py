#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb

import pandas as pd
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    ######################
    # YOUR CODE HERE     #
    ######################

    df = pd.read_csv(artifact_local_path)

    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    logger.info("Dropping outliers")
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    logger.info("Converting columns to the requied formats")
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Drop null values
    df = df.dropna()

    filename = "clean_sample.csv"
    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
     name=args.output_artifact,
     type=args.output_type,
     description=args.output_description,
 )
    artifact.add_file(filename)
    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help='Fully qualified name for the artifact (data before preprocessing)',
        required=True
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help='Name for the W&B artifact (clean data) that will be created',
        required=True
    )

    parser.add_argument(
        "--output_type", 
        type=str,
        help='Type of the artifact (cleaned data) to create',
        required=True
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help='Description for the artifact',
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help='Min value for the price that should be taken into account',
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help='Max value for the price that should be taken into account',
        required=True
    )


    args = parser.parse_args()

    go(args)
