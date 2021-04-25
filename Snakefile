

rule process:
    input:
        costs="results/" + config['run_name'] + "/costs.csv"
    output:
        summary="results/" + config['run_name'] + "/summary.csv"
    #log: "logs/build_powerplants.log"
    threads: 1
    resources: mem=500
    script: "scripts/process.py"
