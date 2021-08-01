
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
        network=expand(config['results_dir'] + config['run'] + "/postnetworks/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}.nc",simpl="",clusters=config['scenario']['clusters'],lv=config['scenario']['lv'],opts="",sector_opts="none",planning_horizons=config['scenario']['planning_horizon']),
        costs="data/costs/costs_{}.csv".format(config['scenario']['planning_horizon']),
        plots=expand(config['results_dir'] + config['run'] + "/maps/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}-costs-all_{planning_horizons}.pdf",simpl="",clusters=45,lv=1.0,opts="",sector_opts="none",planning_horizons=config['scenario']['planning_horizon'])
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
        network=config['results_dir'] + config['run'] + "/prenetworks/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}.nc",
        costs="data/costs/costs_{planning_horizons}.csv"
    output: config['results_dir'] + config['run'] + "/postnetworks/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}.nc"
    shadow: "shallow"
    log:
        solver=config['results_dir'] + config['run'] + "/logs/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}_solver.log",
        python=config['results_dir'] + config['run'] + "/logs/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}_python.log",
        memory=config['results_dir'] + config['run'] + "/logs/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}_memory.log"
    benchmark: config['results_dir'] + config['run'] + "/benchmarks/solve_network/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}"
    threads: 1
    resources: mem_mb=config['solving']['mem']
    script: "scripts/solve_network.py"



rule prepare_sector_network:
    input:
        network='resources/elec_s{simpl}_{clusters}_ec_lv{lv}_{opts}.nc',
        energy_totals_name='resources/energy_totals.csv',
        co2_totals_name='resources/co2_totals.csv',
        transport_name='resources/transport_data.csv',
	traffic_data = "data/emobility/",
        biomass_potentials='resources/biomass_potentials.csv',
        timezone_mappings='data/timezone_mappings.csv',
        heat_profile="data/heat_load_profile_BDEW.csv",
        costs="data/costs/costs_{planning_horizons}.csv",
	h2_cavern = "data/hydrogen_salt_cavern_potentials.csv",
        profile_offwind_ac="resources/profile_offwind-ac.nc",
        profile_offwind_dc="resources/profile_offwind-dc.nc",
        busmap_s="resources/busmap_elec_s{simpl}.csv",
        busmap="resources/busmap_elec_s{simpl}_{clusters}.csv",
        clustered_pop_layout="resources/pop_layout_elec_s{simpl}_{clusters}.csv",
        simplified_pop_layout="resources/pop_layout_elec_s{simpl}.csv",
        industrial_demand="resources/industrial_energy_demand_elec_s{simpl}_{clusters}.csv",
        heat_demand_urban="resources/heat_demand_urban_elec_s{simpl}_{clusters}.nc",
        heat_demand_rural="resources/heat_demand_rural_elec_s{simpl}_{clusters}.nc",
        heat_demand_total="resources/heat_demand_total_elec_s{simpl}_{clusters}.nc",
        temp_soil_total="resources/temp_soil_total_elec_s{simpl}_{clusters}.nc",
        temp_soil_rural="resources/temp_soil_rural_elec_s{simpl}_{clusters}.nc",
        temp_soil_urban="resources/temp_soil_urban_elec_s{simpl}_{clusters}.nc",
        temp_air_total="resources/temp_air_total_elec_s{simpl}_{clusters}.nc",
        temp_air_rural="resources/temp_air_rural_elec_s{simpl}_{clusters}.nc",
        temp_air_urban="resources/temp_air_urban_elec_s{simpl}_{clusters}.nc",
        cop_soil_total="resources/cop_soil_total_elec_s{simpl}_{clusters}.nc",
        cop_soil_rural="resources/cop_soil_rural_elec_s{simpl}_{clusters}.nc",
        cop_soil_urban="resources/cop_soil_urban_elec_s{simpl}_{clusters}.nc",
        cop_air_total="resources/cop_air_total_elec_s{simpl}_{clusters}.nc",
        cop_air_rural="resources/cop_air_rural_elec_s{simpl}_{clusters}.nc",
        cop_air_urban="resources/cop_air_urban_elec_s{simpl}_{clusters}.nc",
        solar_thermal_total="resources/solar_thermal_total_elec_s{simpl}_{clusters}.nc",
        solar_thermal_urban="resources/solar_thermal_urban_elec_s{simpl}_{clusters}.nc",
        solar_thermal_rural="resources/solar_thermal_rural_elec_s{simpl}_{clusters}.nc",
	retro_cost_energy = "resources/retro_cost_elec_s{simpl}_{clusters}.csv",
        floor_area = "resources/floor_area_elec_s{simpl}_{clusters}.csv"
    output: config['results_dir']  +  config['run'] + '/prenetworks/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}.nc'
    threads: 1
    resources: mem_mb=2000
    benchmark: config['results_dir'] + config['run'] + "/benchmarks/prepare_network/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}"
    script: "scripts/prepare_sector_network.py"



rule plot_network:
    input:
        network=config['results_dir'] + config['run'] + "/postnetworks/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}.nc"
    output:
        map=config['results_dir'] + config['run'] + "/maps/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}-costs-all_{planning_horizons}.pdf",
        today=config['results_dir'] + config['run'] + "/maps/elec_s{simpl}_{clusters}_lv{lv}_{opts}_{sector_opts}_{planning_horizons}-today.pdf"
    threads: 2
    resources: mem_mb=10000
    script: "scripts/plot_network.py"
