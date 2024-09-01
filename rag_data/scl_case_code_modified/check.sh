#!/bin/bash

DIRECTORY="."

for json_file in "$DIRECTORY"/*.json; do
    base_name=$(basename "$json_file" .json)
    if [ ! -f "$DIRECTORY/$base_name.scl" ]; then
        echo "$json_file has no scl codes."
    fi
    if [ ! -f "../scl_case_plan_0520_zh_region/$base_name.plan" ]; then
        echo "$json_file has no algos."
    fi
done