
wildcard_constraints:
    lv="[a-z0-9\.]+",
    network="[a-zA-Z0-9]*",
    simpl="[a-zA-Z0-9]*",
    clusters="[0-9]+m?",
    sectors="[+a-zA-Z0-9]+",
    opts="[-+a-zA-Z0-9]*",
    sector_opts="[-+a-zA-Z0-9\.\s]*"


rule all:
    input:
        config['summary_dir'] + '/' + config['run'] + '/' +  config['run'] + '.zip'


rule zip_results:
    input:
        costs=config['summary_dir'] + '/' + config['run'] + '/graphs/costs.pdf'
    output:
        zip=config['summary_dir'] + '/' + config['run'] + '/' +  config['run'] + '.zip'
    threads: 2
    resources: mem_mb=200
    script:
        'scripts/zip_results.py'


rule plot_summary:
    input:
        costs=config['summary_dir'] + '/' + config['run'] + '/csvs/costs.csv',
        energy=config['summary_dir'] + '/' + config['run'] + '/csvs/energy.csv',
        balances=config['summary_dir'] + '/' + config['run'] + '/csvs/supply_energy.csv'
    output:
        costs=config['summary_dir'] + '/' + config['run'] + '/graphs/costs.pdf',
        energy=config['summary_dir'] + '/' + config['run'] + '/graphs/energy.pdf',
        balances=config['summary_dir'] + '/' + config['run'] + '/graphs/balances-energy.pdf'
    threads: 2
    resources: mem_mb=10000
    script:
        'scripts/plot_summary.py'


rule make_summary:
    input:
        network=config['results_dir'] + config['run'] + "/postnetwork.nc",
        costs="data/costs/costs_{}.csv".format(config['scenario']['planning_horizon']),
        plots=config['results_dir'] + config['run'] + "/maps/costs-all.pdf"
    output:
        nodal_costs=config['summary_dir'] + '/' + config['run'] + '/csvs/nodal_costs.csv',
        nodal_capacities=config['summary_dir'] + '/' + config['run'] + '/csvs/nodal_capacities.csv',
        nodal_cfs=config['summary_dir'] + '/' + config['run'] + '/csvs/nodal_cfs.csv',
        cfs=config['summary_dir'] + '/' + config['run'] + '/csvs/cfs.csv',
        costs=config['summary_dir'] + '/' + config['run'] + '/csvs/costs.csv',
        capacities=config['summary_dir'] + '/' + config['run'] + '/csvs/capacities.csv',
        curtailment=config['summary_dir'] + '/' + config['run'] + '/csvs/curtailment.csv',
        energy=config['summary_dir'] + '/' + config['run'] + '/csvs/energy.csv',
        supply=config['summary_dir'] + '/' + config['run'] + '/csvs/supply.csv',
        supply_energy=config['summary_dir'] + '/' + config['run'] + '/csvs/supply_energy.csv',
        prices=config['summary_dir'] + '/' + config['run'] + '/csvs/prices.csv',
        weighted_prices=config['summary_dir'] + '/' + config['run'] + '/csvs/weighted_prices.csv',
        market_values=config['summary_dir'] + '/' + config['run'] + '/csvs/market_values.csv',
        price_statistics=config['summary_dir'] + '/' + config['run'] + '/csvs/price_statistics.csv',
        metrics=config['summary_dir'] + '/' + config['run'] + '/csvs/metrics.csv'
    threads: 2
    resources: mem_mb=10000
    script:
        'scripts/make_summary.py'


rule solve_network:
    input:
        network=config['results_dir'] + config['run'] + "/prenetwork.nc",
        costs="data/costs/costs_{}.csv".format(config['scenario']['planning_horizon'])
    output: config['results_dir'] + config['run'] + "/postnetwork.nc"
    shadow: "shallow"
    log:
        solver=config['results_dir'] + config['run'] + "/logs/solver.log",
        python=config['results_dir'] + config['run'] + "/logs/python.log",
        memory=config['results_dir'] + config['run'] + "/logs/memory.log"
    benchmark: config['results_dir'] + config['run'] + "/benchmarks/solve_network/benchmark"
    threads: 1
    resources: mem_mb=config['solving']['mem']
    script: "scripts/solve_network.py"



rule prepare_sector_network:
    input:
        network='resources/elec_s_{}_ec_lv{}_.nc'.format(config['scenario']['clusters'],config['scenario']['lv']),
        energy_totals_name='resources/energy_totals.csv',
        co2_totals_name='resources/co2_totals.csv',
        transport_name='resources/transport_data.csv',
	traffic_data = "data/emobility/",
        biomass_potentials='resources/biomass_potentials.csv',
        timezone_mappings='data/timezone_mappings.csv',
        heat_profile="data/heat_load_profile_BDEW.csv",
        costs="data/costs/costs_{}.csv".format(config['scenario']['planning_horizon']),
	h2_cavern = "data/hydrogen_salt_cavern_potentials.csv",
        profile_offwind_ac="resources/profile_offwind-ac.nc",
        profile_offwind_dc="resources/profile_offwind-dc.nc",
        busmap_s="resources/busmap_elec_s.csv",
        busmap="resources/busmap_elec_s_{}.csv".format(config['scenario']['clusters']),
        clustered_pop_layout="resources/pop_layout_elec_s_{}.csv".format(config['scenario']['clusters']),
        simplified_pop_layout="resources/pop_layout_elec_s.csv",
        industrial_demand="resources/industrial_energy_demand_elec_s_{}.csv".format(config['scenario']['clusters']),
        heat_demand_urban="resources/heat_demand_urban_elec_s_{}.nc".format(config['scenario']['clusters']),
        heat_demand_rural="resources/heat_demand_rural_elec_s_{}.nc".format(config['scenario']['clusters']),
        heat_demand_total="resources/heat_demand_total_elec_s_{}.nc".format(config['scenario']['clusters']),
        temp_soil_total="resources/temp_soil_total_elec_s_{}.nc".format(config['scenario']['clusters']),
        temp_soil_rural="resources/temp_soil_rural_elec_s_{}.nc".format(config['scenario']['clusters']),
        temp_soil_urban="resources/temp_soil_urban_elec_s_{}.nc".format(config['scenario']['clusters']),
        temp_air_total="resources/temp_air_total_elec_s_{}.nc".format(config['scenario']['clusters']),
        temp_air_rural="resources/temp_air_rural_elec_s_{}.nc".format(config['scenario']['clusters']),
        temp_air_urban="resources/temp_air_urban_elec_s_{}.nc".format(config['scenario']['clusters']),
        cop_soil_total="resources/cop_soil_total_elec_s_{}.nc".format(config['scenario']['clusters']),
        cop_soil_rural="resources/cop_soil_rural_elec_s_{}.nc".format(config['scenario']['clusters']),
        cop_soil_urban="resources/cop_soil_urban_elec_s_{}.nc".format(config['scenario']['clusters']),
        cop_air_total="resources/cop_air_total_elec_s_{}.nc".format(config['scenario']['clusters']),
        cop_air_rural="resources/cop_air_rural_elec_s_{}.nc".format(config['scenario']['clusters']),
        cop_air_urban="resources/cop_air_urban_elec_s_{}.nc".format(config['scenario']['clusters']),
        solar_thermal_total="resources/solar_thermal_total_elec_s_{}.nc".format(config['scenario']['clusters']),
        solar_thermal_urban="resources/solar_thermal_urban_elec_s_{}.nc".format(config['scenario']['clusters']),
        solar_thermal_rural="resources/solar_thermal_rural_elec_s_{}.nc".format(config['scenario']['clusters']),
	retro_cost_energy = "resources/retro_cost_elec_s_{}.csv".format(config['scenario']['clusters']),
        floor_area = "resources/floor_area_elec_s_{}.csv".format(config['scenario']['clusters'])
    output: config['results_dir']  +  config['run'] + '/prenetwork.nc'
    threads: 1
    resources: mem_mb=2000
    benchmark: config['results_dir'] + config['run'] + "/benchmarks/prepare_network/benchmark"
    script: "scripts/prepare_sector_network.py"



rule plot_network:
    input:
        network=config['results_dir'] + config['run'] + "/postnetwork.nc"
    output:
        map=config['results_dir'] + config['run'] + "/maps/costs-all.pdf",
        today=config['results_dir'] + config['run'] + "/maps/today.pdf"
    threads: 2
    resources: mem_mb=10000
    script: "scripts/plot_network.py"
