

import pandas as pd

costs = pd.read_csv(snakemake.input.costs,index_col=0,sep=",")

print(costs)

print(snakemake.config)

if snakemake.config["rooftop"]:
    costs *= 2

costs.to_csv(snakemake.output.summary)
