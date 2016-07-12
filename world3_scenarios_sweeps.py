import os
import sys
import logging #en reemplazo de los prints
logger = logging.getLogger("--World3 scenarios sweep--") #un logger especifico para este modulo
# Mine:
import mos_writer.mos_script_factory as mos_script_factory
import sweeping.run_and_plot_model as run_and_plot_model
import filesystem.files_aux as files_aux
import settings.settings_world3_sweep as world3_settings

#Aux for GLOBALS:
## Skeletons of sweep_value_formula_str. Free variable: i (goes from 0 to (iterations-1) ):
_increasing_by_increment_from_initial_skeleton = "{initial} + i*{increment}"
_increasing_by_percentage_from_initial_skeleton = "{initial}*({percentage}/100*i+1)"
def deltaBeforeAndAfter(p,iterations,delta): #Have to create a function for "delta_before_and_after" because I have to convert to int in python and not in the Modelica Scripting Language
    iterations_div_2_int = int(iterations/2)
    return "{p}*(1-{iterations_div_2_int}*{delta}) + {p}*({delta}*i)".format(p=p,iterations_div_2_int=iterations_div_2_int,delta=delta)
## Examples:
# sweep_value_formula_str = _increasing_by_increment_from_initial_skeleton.format(initial=2012,increment=10) # "2012 + i*10" --> 2012,2022,2032...
# sweep_value_formula_str = _increasing_by_percentage_from_initial_skeleton.format(initial=1e12,percentage=20) # "1e12*((20/100)*i+1)" --> 1e12, 1.2e12, 1.4e12 ...
# sweep_value_formula_str = deltaBeforeAndAfter(p=10,delta=0.01,iterations=7) # '10*(1-3*0.01) + 10*(0.01*i)' --> 9.7, 9.8, 9.9, 10, 10.1, 10.2, 10.3
# Special sweeps constants definitions: DON'T CHANGE ANYTHING
SPECIAL_policy_years = None # Special vars sweeping that sweeps the year to apply the different policies respective of each scenario. (each scenario has it's policies to apply.)

def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    # testPolicyYears()
    # testDeltaNRResources()
    # testFertility()
    # testFertility2()
    # standardRun()
# The vermeulen tests need a modified SystemDynamics .mo!
    # testVermeulenAndJonghRun2() #Run1 is Meadows' std run
    # testVermeulenAndJonghRun3()
# From IDA sens analysis:
    # testDeltaAvgLifeInd()
    testDeltaIncomeExpectAvgTime()
    # testDeltaHlthServImpactDel()
    # testDeltaFrCapAlObtRes2Bracket5Bracket()


## Predefined tests
def testVermeulenAndJonghRun2():
    #The first run (for now we have to plot each run separately)
    kwargs = {
# "plot_vars":["population","ppoll_index","industrial_output","nr_resources"],#,"nr_resources","Population_Dynamics1FFW"] #without the "." in "...Dynamics.FFW" because numpy doesn't play well with dots in column names
    "plot_vars":[#"pseudo" parameters:
                 "Industrial_Investment1Industrial_Outputs_ind_cap_out_ratio", "Industrial_Investment1S_FIOA_Conss_fioa_cons_const","Industrial_Investment1S_Avg_Life_Ind_Caps_avg_life_ind_cap",
                 "population","ppoll_index","industrial_output","nr_resources"],#,"nr_resources","Population_Dynamics1FFW"] #without the "." in "...Dynamics.FFW" because numpy doesn't play well with dots in column names
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1] ,#List of ints representing the scenarios to run (from 1 to 11).  Example: [1,2,3,4,5,6,7,8,9]
    "iterations" : 1 ,#No sweeping: more than one iteration is irrelevant
    "sweep_vars": [] ,#No sweeping done in VermeulenAndJonghRun
    "sweep_value_formula_str" : "i" ,#irrelevant formula (no sweeping)
    "fixed_params" : [  # Params changes that will be fixed throughout the sweep. Example: [("nr_resources_init",2e12)]
            # ("p_ind_cap_out_ratio_1",3.3),   #V&J-2: ICOR= 3.3, Default: ICOR=3
            # ("p_fioa_cons_const_1",0.473),   #V&J-2: FIOAC= 0.473, Default: FIOAC=0.43
            # ("p_avg_life_ind_cap_1", 12.6),  #V&J-2: ALIC= 12.6, Default: ALIC=14
                   ],
    }

    setUpSweepsAndRun(**kwargs)

def standardRun(): #ONLY TO GET THE STANDARD CSV!
    kwargs = {
    "plot_vars":["population","Population_Dynamics1pop_state_var_new"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2200  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : 1, #More than one iteration is irrelevant
    "sweep_vars": [] ,#No sweeping done in std run
    "sweep_value_formula_str" : "i" ,#irrelevant formula (no sweeping)
    "fixed_params" : [], #We don't want to change any parameters
    }
    setUpSweepsAndRun(**kwargs)

def testFertility2():
    kwargs = {
    "plot_vars":[],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : 8, #More than one iteration is irrelevant
    "sweep_vars":  ["pseudo_ffw"], #NOT ORIGINAL PARAMETER! ADDED ONLY TO SCENARIO 1
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=1,delta=0.01,iterations=iterations), #Has to be a string with only free variable "i"
    "fixed_params" : [
            ("p_ind_cap_out_ratio_1",3.15),   #Hugo: ICOR= 3.15, Default: ICOR=3
            ("p_avg_life_ind_cap_1", 13.3),   #Hugo: ALIC= 13.3, Default: ALIC=14
            ("p_avg_life_serv_cap_1", 17.1),  #Hugo: ALSC= 17.1, Default: ALSC=20
            ("p_serv_cap_out_ratio_1", 1.05)  #Hugo: SCOR= 1.05, Default: SCOR=1
        ],
    }
    setUpSweepsAndRun(**kwargs)

def testFertility():
    kwargs = {
    "plot_vars":[],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : 12,
    "sweep_vars":  ["max_tot_fert_norm"], #NOT ORIGINAL PARAMETER! ADDED ONLY TO SCENARIO 1
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=12,delta=0.1,iterations=iterations), #Has to be a string with only free variable "i"
    "fixed_params" : [
       ("p_ind_cap_out_ratio_1",3.15),   #Hugo: ICOR= 3.15, Default: ICOR=3  
       ("p_avg_life_ind_cap_1", 13.3),   #Hugo: ALIC= 13.3, Default: ALIC=14 
       ("p_avg_life_serv_cap_1", 17.1),  #Hugo: ALSC= 17.1, Default: ALSC=20 
       ("p_serv_cap_out_ratio_1", 1.05)  #Hugo: SCOR= 1.05, Default: SCOR=1  
        ],
    }

    setUpSweepsAndRun(**kwargs)

def testDeltaFrCapAlObtRes2Bracket5Bracket():
    iterations = 10;
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["p_fr_cap_al_obt_res_2[5]"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=0.05,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaHlthServImpactDel():
    iterations = 5;
    kwargs = {
    "plot_vars":["Food_Production1Agr_InpIntegrator1y","population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["hlth_serv_impact_del"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=20,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaIncomeExpectAvgTime():
    iterations = 10;
    kwargs = {
    "plot_vars":["Population_Dynamics1Pop_0_14y","population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["income_expect_avg_time"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=3,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaAvgLifeInd():
    iterations = 5;
    kwargs = {
    "plot_vars":["Population_Dynamics1Pop_0_14y","population"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2500  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : iterations,
    "sweep_vars":  ["p_avg_life_ind_cap_1"], # Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=14,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    }
    setUpSweepsAndRun(**kwargs)
def testDeltaNRResources():
    kwargs = {
    "plot_vars":[],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2100  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [1], #The standard run corresponds to the first scenario
    "iterations" : 10,
    "sweep_vars":  ["nr_resources_init"], # Sweep only one var: "nr_resources_init". Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : deltaBeforeAndAfter(p=1e12,delta=0.1,iterations=iterations), # Sweep floor(iterations/2) times before and after p changing by a percentage of delta*100
    "fixed_params" : [],  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    }
    setUpSweepsAndRun(**kwargs)

def testPolicyYears():
    kwargs = {
    "plot_vars":["population","nr_resources"],
    "startTime": 1900 ,# year to start the simulation (1900 example)
    "stopTime": 2200  ,# year to end the simulation (2100 for example)
    "scens_to_run" : [9],
    "iterations" : 1,
    "sweep_vars":  SPECIAL_policy_years, # Set to SPECIAL_policy_years to use scenario specific defaults (year of application of policies). Examples: SPECIAL_policy_years, ["nr_resources_init"]
    "sweep_value_formula_str" : _increasing_by_increment_from_initial_skeleton.format(initial=2022,increment=10), # "2012 + i*10" --> 2012,2022,2032...
    "fixed_params" : []  # No fixed parameter changes. Example: [("nr_resources_init",6.3e9),("des_compl_fam_size_norm",2),...]
    }
    setUpSweepsAndRun(**kwargs)

#World3 specific:
def setUpSweepsAndRun(iterations,sweep_vars,sweep_value_formula_str,fixed_params,plot_vars,startTime,stopTime,scens_to_run):
    #The "root" output folder path.
    output_path = files_aux.makeOutputPath()
    #Create scenarios from factory
    scenarios = []
    for i in scens_to_run:
        initial_factory_for_scen_i = initialFactoryForWorld3Scenario(scen_num=i,start_time=startTime,stop_time=stopTime,fixed_params=fixed_params,sweep_vars=sweep_vars)
        scenario_tuple =("scenario_"+str(i),initial_factory_for_scen_i)
        scenarios.append(scenario_tuple)
    doScenariosSet(scenarios, plot_vars=plot_vars,iterations=iterations,output_root_path=output_path, sweep_value_formula_str=sweep_value_formula_str)
def doScenariosSet(scenarios,plot_vars,iterations,output_root_path,sweep_value_formula_str):
    for folder_name,initial_scen_factory in scenarios:
        logger.debug("Running scenario {folder_name}".format(folder_name=folder_name))
        os.makedirs(os.path.join(output_root_path,folder_name))
        run_and_plot_model.createSweepRunAndPlotForModelInfo(initial_scen_factory,plot_vars=plot_vars,iterations=iterations,output_folder_path=os.path.join(output_root_path,folder_name),sweep_value_formula_str=sweep_value_formula_str,csv_file_name_modelica_skeleton=world3_settings.csv_file_name_modelica_skeleton,csv_file_name_python_skeleton=world3_settings.csv_file_name_python_skeleton  )
def initialFactoryForWorld3Scenario(scen_num,start_time,stop_time,sweep_vars=None,fixed_params=[]):
    initial_factory_for_scen_1 = initialFactoryForWorld3Scenario
    #Get the mos script factory for a scenario number (valid from 1 to 11)
    assert 1<=scen_num<=9 , "The scenario number must be between 1 and 9. Your input: {0}".format(scen_num)
    if sweep_vars or isinstance(sweep_vars,list): #Have to use isinstance for empty lists
        #If given a list of variables to sweep, don't use defaults
        final_sweep_vars = sweep_vars
    else:
        #If NOT given a list of variables to sweep, use the defaults for that scenario
        final_sweep_vars = defaultSweepVarsForScenario(scen_num)
    model_name = world3_settings._world3_scenario_model_skeleton.format(scen_num=scen_num) #global
    initial_factory_dict = {
        #"mo_file"     : world3_settings._sys_dyn_package_path.replace("\\","/"), #Global
        #"mo_file"     :  world3_settings._sys_dyn_package_pw_fix_path.replace("\\","/"), #Global
        # "mo_file"     :  world3_settings._sys_dyn_package_vanilla_path.replace("\\","/"), #Global
        "mo_file"     :  world3_settings._sys_dyn_package_pop_state_var_new.replace("\\","/"), #Global

        "sweep_vars"  : final_sweep_vars,
        "model_name"  : model_name,
        "startTime"   : start_time,
        "stopTime"    : stop_time,
        "fixed_params": fixed_params,
        }
    initial_factory = mos_script_factory.MosScriptFactory(initial_factory_dict)
    return initial_factory
def defaultSweepVarsForScenario(scen_num):
    default_sweep_vars_dict = defaultSweepVarsDict()
    return default_sweep_vars_dict[scen_num]
def defaultSweepVarsDict():
    default_sweep_vars_dict ={
            9: ["t_fcaor_time", "t_fert_cont_eff_time", "t_zero_pop_grow_time", "t_ind_equil_time", "t_policy_year", "t_land_life_time"],
            8: ["t_fcaor_time", "t_fert_cont_eff_time", "t_zero_pop_grow_time", "t_ind_equil_time", "t_policy_year"],
            7: ["t_fcaor_time", "t_fert_cont_eff_time", "t_zero_pop_grow_time"],
            6: ["t_fcaor_time", "t_policy_year", "t_land_life_time"],
            5: ["t_fcaor_time", "t_policy_year", "t_land_life_time"],
            4: ["t_fcaor_time", "t_policy_year"],
            3: ["t_fcaor_time", "t_policy_year"],
            2: ["t_fcaor_time"],
            1: []
            }
    return default_sweep_vars_dict

# FIRST EXECUTABLE CODE:
if __name__ == "__main__":
    main()