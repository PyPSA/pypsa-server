

import numpy as np
import pandas as pd

#allow plotting without Xwindows
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

#consolidate and rename
def rename_techs(label):

    prefix_to_remove = ["residential ","services ","urban ","rural ","central ","decentral "]

    rename_if_contains = ["biomass CHP","gas CHP","gas boiler","biogas","solar thermal","air heat pump","ground heat pump","resistive heater","Fischer-Tropsch"]

    rename_if_contains_dict = {"water tanks" : "hot water storage",
                               "retrofitting" : "building retrofitting",
                               "battery" : "battery storage",
                               "CC" : "CC"}

    rename = {"solar" : "solar PV utility",
              "solar rooftop" : "solar PV rooftop",
              "Sabatier" : "methanation",
              "offwind" : "offshore wind",
              "offwind-ac" : "offshore wind (AC)",
              "offwind-dc" : "offshore wind (DC)",
              "onwind" : "onshore wind",
              "ror" : "hydroelectricity",
              "hydro" : "hydroelectricity",
              "PHS" : "hydroelectricity",
              "co2 Store" : "DAC",
              "co2 stored" : "CO2 sequestration",
              "H2" : "hydrogen storage",
              "electricity" : "non-industrial electricity",
              "gas" : "fossil gas",
              "oil" : "fossil oil",
              "AC" : "transmission lines",
              "DC" : "transmission lines",
              "B2B" : "transmission lines"}

    for ptr in prefix_to_remove:
        if label[:len(ptr)] == ptr:
            label = label[len(ptr):]

    for rif in rename_if_contains:
        if rif in label:
            label = rif

    for old,new in rename_if_contains_dict.items():
        if old in label:
            label = new

    for old,new in rename.items():
        if old == label:
            label = new
    return label


preferred_order = pd.Index(["transmission lines","electricity distribution grid","hydroelectricity","hydro reservoir","run of river","pumped hydro storage","solid biomass","biogas","oil","fossil oil","nuclear","uranium","nuclear heat","onshore wind","offshore wind","offshore wind (AC)","offshore wind (DC)","solar PV utility","solar PV rooftop","solar thermal","solar","building retrofitting","ground heat pump","ambient ground heat","air heat pump","ambient air heat","heat pump","resistive heater","power-to-heat","gas-to-power/heat","biomass CHP","gas CHP","CHP","OCGT","gas boiler","gas","fossil gas","natural gas","helmeth","methanation","hydrogen storage","H2 Electrolysis","H2 Fuel Cell","H2 pipeline","power-to-gas","power-to-liquid","battery storage","hot water storage","CO2 sequestration"])

def plot_costs():


    cost_df = pd.read_csv(snakemake.input.costs,index_col=list(range(3)),header=list(range(n_header)))


    df = cost_df.groupby(cost_df.index.get_level_values(2)).sum()

    #convert to billions
    df = df/1e9

    df = df.groupby(df.index.map(rename_techs)).sum()

    to_drop = df.index[df.max(axis=1) < snakemake.config['plotting']['costs_threshold']*df.sum().max()]

    print("dropping")

    print(df.loc[to_drop])

    df = df.drop(to_drop)

    print(df.sum())

    new_index = preferred_order.intersection(df.index).append(df.index.difference(preferred_order))

    new_columns = df.sum().sort_values().index

    fig, ax = plt.subplots()
    fig.set_size_inches((12,8))

    df.loc[new_index,new_columns].T.plot(kind="bar",ax=ax,stacked=True,color=[snakemake.config['plotting']['tech_colors'][i] for i in new_index])


    handles,labels = ax.get_legend_handles_labels()

    handles.reverse()
    labels.reverse()

    ax.set_ylim([0,snakemake.config['plotting']['costs_max']])

    ax.set_ylabel("System Cost [EUR billion per year]")

    ax.set_xlabel("")

    ax.grid(axis="y")

    ax.legend(handles,labels,ncol=4,loc="upper left")


    fig.tight_layout()

    fig.savefig(snakemake.output.costs,transparent=True)
    fig.savefig(snakemake.output.costs.replace("pdf","png"),transparent=True)


def plot_capacities():

    df = pd.read_csv(snakemake.input.capacities,index_col=list(range(2)),header=list(range(n_header)))


    df = df.groupby(level=1).sum()

    #convert to GW
    df = df/1e3

    df = df.groupby(df.index.map(rename_techs)).sum()

    selection = ["gas CHP","biomass CHP","H2 Fuel Cell","OCGT","nuclear","solar PV rooftop","solar PV utility","offshore wind (DC)","offshore wind (AC)","onshore wind","hydroelectricity","Fischer-Tropsch","H2 Electrolysis","resistive heater","air heat pump","ground heat pump"]

    df = df.loc[[s for s in selection if s in df.index]]

    fig, ax = plt.subplots()
    fig.set_size_inches((12,8))

    s = df.iloc[:,0]

    s.plot(kind="bar",ax=ax,color=[snakemake.config['plotting']['tech_colors'][i] for i in s.index])


    handles,labels = ax.get_legend_handles_labels()

    handles.reverse()
    labels.reverse()

    ax.set_ylim([0,1.1*s.max()])

    ax.set_ylabel("capacity [GW$_{el}$]")

    ax.set_xlabel("")

    ax.grid(axis="y")

    ax.legend(handles,labels,ncol=4,loc="upper left")


    fig.tight_layout()

    fig.savefig(snakemake.output.capacities,transparent=True)
    fig.savefig(snakemake.output.capacities.replace("pdf","png"),transparent=True)


def plot_energy():

    energy_df = pd.read_csv(snakemake.input.energy,index_col=list(range(2)),header=list(range(n_header)))

    df = energy_df.groupby(energy_df.index.get_level_values(1)).sum()

    #convert MWh to TWh
    df = df/1e6

    df = df.groupby(df.index.map(rename_techs)).sum()

    to_drop = df.index[df.abs().max(axis=1) < snakemake.config['plotting']['energy_threshold']*df.abs().sum().max()]

    print("dropping")

    print(df.loc[to_drop])

    df = df.drop(to_drop)

    print(df.sum())

    print(df)

    new_index = preferred_order.intersection(df.index).append(df.index.difference(preferred_order))

    new_columns = df.columns.sort_values()
    #new_columns = df.sum().sort_values().index
    fig, ax = plt.subplots()
    fig.set_size_inches((12,8))

    print(df.loc[new_index,new_columns])

    df.loc[new_index,new_columns].T.plot(kind="bar",ax=ax,stacked=True,color=[snakemake.config['plotting']['tech_colors'][i] for i in new_index])


    handles,labels = ax.get_legend_handles_labels()

    handles.reverse()
    labels.reverse()

    ax.set_ylim([snakemake.config['plotting']['energy_min'],snakemake.config['plotting']['energy_max']])

    ax.set_ylabel("Energy [TWh/a]")

    ax.set_xlabel("")

    ax.grid(axis="y")

    ax.legend(handles,labels,ncol=4,loc="upper left")


    fig.tight_layout()

    fig.savefig(snakemake.output.energy,transparent=True)
    fig.savefig(snakemake.output.energy.replace("pdf","png"),transparent=True)



def plot_balances():

    co2_carriers = ["co2","co2 stored","process emissions"]

    balances_df = pd.read_csv(snakemake.input.balances,index_col=list(range(3)),header=list(range(n_header)))

    balances = {i.replace(" ","_") : [i] for i in balances_df.index.levels[0]}
    balances["energy"] = balances_df.index.levels[0].symmetric_difference(co2_carriers)

    for k,v in balances.items():

        df = balances_df.loc[v]
        df = df.groupby(df.index.get_level_values(2)).sum()

        #convert MWh to TWh
        df = df/1e6

        #remove trailing link ports
        df.index = [i[:-1] if ((i != "co2") and (i[-1:] in ["0","1","2","3"])) else i for i in df.index]

        df = df.groupby(df.index.map(rename_techs)).sum()

        to_drop = df.index[df.abs().max(axis=1) < snakemake.config['plotting']['energy_threshold']/10]

        print("dropping")

        print(df.loc[to_drop])

        df = df.drop(to_drop)

        print(df.sum())

        if df.empty:
            continue

        new_index = preferred_order.intersection(df.index).append(df.index.difference(preferred_order))

        new_columns = df.columns.sort_values()


        fig, ax = plt.subplots()
        fig.set_size_inches((12,8))

        df.loc[new_index,new_columns].T.plot(kind="bar",ax=ax,stacked=True,color=[snakemake.config['plotting']['tech_colors'][i] for i in new_index])


        handles,labels = ax.get_legend_handles_labels()

        handles.reverse()
        labels.reverse()

        if v[0] in co2_carriers:
            ax.set_ylabel("CO2 [MtCO2/a]")
        else:
            ax.set_ylabel("Energy [TWh/a]")

        ax.set_xlabel("")

        ax.grid(axis="y")

        ax.legend(handles,labels,ncol=4,loc="upper left")


        fig.tight_layout()

        fig.savefig(snakemake.output.balances[:-10] + k + ".pdf",transparent=True)
        fig.savefig(snakemake.output.balances[:-10] + k + ".png",transparent=True)

def historical_emissions(cts):
    """
    read historical emissions to add them to the carbon budget plot
    """
    #https://www.eea.europa.eu/data-and-maps/data/national-emissions-reported-to-the-unfccc-and-to-the-eu-greenhouse-gas-monitoring-mechanism-16
    #downloaded 201228 (modified by EEA last on 201221)
    fn = "data/eea/UNFCCC_v23.csv"
    df = pd.read_csv(fn, encoding="latin-1")
    df.loc[df["Year"] == "1985-1987","Year"] = 1986
    df["Year"] = df["Year"].astype(int)
    df = df.set_index(['Year', 'Sector_name', 'Country_code', 'Pollutant_name']).sort_index()

    e = pd.Series()
    e["electricity"] = '1.A.1.a - Public Electricity and Heat Production'
    e['residential non-elec'] = '1.A.4.b - Residential'
    e['services non-elec'] = '1.A.4.a - Commercial/Institutional'
    e['rail non-elec'] = "1.A.3.c - Railways"
    e["road non-elec"] = '1.A.3.b - Road Transportation'
    e["domestic navigation"] = "1.A.3.d - Domestic Navigation"
    e['international navigation'] = '1.D.1.b - International Navigation'
    e["domestic aviation"] = '1.A.3.a - Domestic Aviation'
    e["international aviation"] = '1.D.1.a - International Aviation'
    e['total energy'] = '1 - Energy'
    e['industrial processes'] = '2 - Industrial Processes and Product Use'
    e['agriculture'] = '3 - Agriculture'
    e['LULUCF'] = '4 - Land Use, Land-Use Change and Forestry'
    e['waste management'] = '5 - Waste management'
    e['other'] = '6 - Other Sector'
    e['indirect'] = 'ind_CO2 - Indirect CO2'
    e["total wL"] = "Total (with LULUCF)"
    e["total woL"] = "Total (without LULUCF)"

    pol = ["CO2"] # ["All greenhouse gases - (CO2 equivalent)"]
    cts
    if "GB" in cts:
        cts.remove("GB")
        cts.append("UK")

    year = np.arange(1990,2018).tolist()

    idx = pd.IndexSlice
    co2_totals = df.loc[idx[year,e.values,cts,pol],"emissions"].unstack("Year").rename(index=pd.Series(e.index,e.values))

    co2_totals = (1/1e6)*co2_totals.groupby(level=0, axis=0).sum() #Gton CO2

    co2_totals.loc['industrial non-elec'] = co2_totals.loc['total energy'] - co2_totals.loc[['electricity', 'services non-elec','residential non-elec', 'road non-elec',
                                                                              'rail non-elec', 'domestic aviation', 'international aviation', 'domestic navigation',
                                                                              'international navigation']].sum()

    emissions = co2_totals.loc["electricity"]
    if "T" in opts:
        emissions += co2_totals.loc[[i+ " non-elec" for i in ["rail","road"]]].sum()
    if "H" in opts:
        emissions += co2_totals.loc[[i+ " non-elec" for i in ["residential","services"]]].sum()
    if "I" in opts:
        emissions += co2_totals.loc[["industrial non-elec","industrial processes",
                                          "domestic aviation","international aviation",
                                          "domestic navigation","international navigation"]].sum()
    return emissions



if __name__ == "__main__":
    # Detect running outside of snakemake and mock snakemake for testing
    if 'snakemake' not in globals():
        from vresutils import Dict
        import yaml
        snakemake = Dict()
        with open('config.yaml', encoding='utf8') as f:
            snakemake.config = yaml.safe_load(f)
        snakemake.input = Dict()
        snakemake.output = Dict()
        snakemake.wildcards = Dict()
        #snakemake.wildcards['sector_opts']='3H-T-H-B-I-solar3-dist1-cb48be3'

        for item in ["costs", "energy"]:
            snakemake.input[item] = snakemake.config['summary_dir'] + '/{name}/csvs/{item}.csv'.format(name=snakemake.config['run'],item=item)
            snakemake.output[item] = snakemake.config['summary_dir'] + '/{name}/graphs/{item}.pdf'.format(name=snakemake.config['run'],item=item)
        snakemake.input["balances"] = snakemake.config['summary_dir'] + '/{name}/csvs/supply_energy.csv'.format(name=snakemake.config['run'],item=item)
        snakemake.output["balances"] = snakemake.config['summary_dir'] + '/{name}/graphs/balances-energy.csv'.format(name=snakemake.config['run'],item=item)


    n_header = 1

    plot_costs()

    plot_capacities()

    plot_energy()

    plot_balances()
