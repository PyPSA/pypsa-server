
import pypsa, pandas as pd, numpy as np

from plot_summary import rename_techs, preferred_order


override_component_attrs = pypsa.descriptors.Dict({k : v.copy() for k,v in pypsa.components.component_attrs.items()})
override_component_attrs["Link"].loc["bus2"] = ["string",np.nan,np.nan,"2nd bus","Input (optional)"]
override_component_attrs["Link"].loc["bus3"] = ["string",np.nan,np.nan,"3rd bus","Input (optional)"]
override_component_attrs["Link"].loc["bus4"] = ["string",np.nan,np.nan,"4th bus","Input (optional)"]
override_component_attrs["Link"].loc["efficiency2"] = ["static or series","per unit",1.,"2nd bus efficiency","Input (optional)"]
override_component_attrs["Link"].loc["efficiency3"] = ["static or series","per unit",1.,"3rd bus efficiency","Input (optional)"]
override_component_attrs["Link"].loc["efficiency4"] = ["static or series","per unit",1.,"4th bus efficiency","Input (optional)"]
override_component_attrs["Link"].loc["p2"] = ["series","MW",0.,"2nd bus output","Output"]
override_component_attrs["Link"].loc["p3"] = ["series","MW",0.,"3rd bus output","Output"]
override_component_attrs["Link"].loc["p4"] = ["series","MW",0.,"4th bus output","Output"]
override_component_attrs["StorageUnit"].loc["p_dispatch"] = ["series","MW",0.,"Storage discharging.","Output"]
override_component_attrs["StorageUnit"].loc["p_store"] = ["series","MW",0.,"Storage charging.","Output"]


def export_time_series(network_filename, time_series_filename):

    n = pypsa.Network(network_filename,
                      override_component_attrs=override_component_attrs)

    #stores need more descriptive names
    n.stores["carrier"].replace("H2","hydrogen storage",inplace=True)
    n.stores["carrier"].replace("gas","gas storage",inplace=True)
    n.stores["carrier"].replace("oil","oil storage",inplace=True)
    n.stores["carrier"].replace("co2","CO2 atmosphere",inplace=True)

    bus_carriers = n.buses.carrier.unique()

    all_carrier_dict = {}

    for i in bus_carriers:
        bus_map = (n.buses.carrier == i)
        bus_map.at[""] = False

        carrier_df = pd.DataFrame(index=n.snapshots,
                                  dtype=float)

        for c in n.iterate_components(n.one_port_components):

            items = c.df.index[c.df.bus.map(bus_map).fillna(False)]

            if len(items) == 0:
                continue

            s = c.pnl.p[items].multiply(c.df.loc[items,'sign'],axis=1).groupby(c.df.loc[items,'carrier'],axis=1).sum()
            carrier_df = pd.concat([carrier_df,s],axis=1)

        for c in n.iterate_components(n.branch_components):

            for end in [col[3:] for col in c.df.columns if col[:3] == "bus"]:

                items = c.df.index[c.df["bus" + str(end)].map(bus_map,na_action=False)]

                if len(items) == 0:
                    continue

                s = (-1)*c.pnl["p"+end][items].groupby(c.df.loc[items,'carrier'],axis=1).sum()
                s.columns = s.columns+end
                carrier_df = pd.concat([carrier_df,s],axis=1)

        all_carrier_dict[i] = carrier_df

    all_carrier_df = pd.concat(all_carrier_dict, axis=1)
    print(all_carrier_df)

    all_carrier_df.round(1).to_csv(time_series_filename)


if __name__ == "__main__":
    if "snakemake" not in globals():
        from vresutils.snakemake import MockSnakemake, Dict

        #has 5 snapshots
        jobid = "4f0cf60e-fecd-49d6-95ea-e38a4bfeb242"
        #has 2920 snapshots
        jobid = "8bd53e43-a32f-4af7-ba9a-cdf7e38b4f9d"

        snakemake = MockSnakemake(
            input=dict(network=[f"static/results/{jobid}/postnetworks/elec_s_45_lvopt__none_2050.nc"]),
            output=dict(series=f"static/results/{jobid}/csvs/series.csv"))

    print(snakemake.input.network[0], snakemake.output.series)
    export_time_series(snakemake.input.network[0], snakemake.output.series)
