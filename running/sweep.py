# Std
import numpy
import itertools
import os
# Mine
import modelica_interface.build_model as build_model
import filesystem.files_aux as files_aux
import running.simulation_run_info as simu_run_info
import sys

import logging
filehandler = logging.FileHandler("/home/omsens/Documents/results_experiments/logging/todo.log")
logger = logging.getLogger("multiparam_sweep")
logger.addHandler(filehandler)
logger.setLevel(logging.DEBUG)


class ParametersSweeper:
    def __init__(self, model_name, model_file_path, start_time, stop_time, perturbation_info_per_param, fixed_params,
                 build_folder_path, base_dir, results_dirname, 
                 number_of_intervals=300):
        logger.debug("initializing parameters sweeper")
        # Save args
        self.model_name = model_name
        self.model_file_path = model_file_path
        self.start_time = start_time
        self.stop_time = stop_time
        self.perturbation_info_per_param = perturbation_info_per_param
        self.fixed_params_raw = fixed_params
        # Initialize builder
        self.model_builder = build_model.ModelicaModelBuilder(model_name, start_time, stop_time, model_file_path,
                                                              number_of_intervals)
        # Build model
        self.compiled_model = self.model_builder.buildToFolderPath(build_folder_path, base_dir, results_dirname)
        logger.debug("builde 4")
        # Get the default values for the params to perturb using the compiled model
        self.params_defaults = self.defaultValuesForParamsToPerturb(self.compiled_model)
        logger.debug("builde 5")
        # Calculate the sweep values per param
        self.sweep_values_per_param = sweepValuesPerParamFromParamsInfos(self.params_defaults,
                                                                         self.perturbation_info_per_param)
        logger.debug("builder 6")
        # Parse the fixed params
        self.fixed_params = perturbationInfoForFixedParams(self.params_defaults, self.fixed_params_raw)
        logger.debug("finish initialization sweeper")

    def runSweep(self, dest_folder_path, communicator=None, simu_flags=""):
        logger.debug("runSweep")
        # Make folder for runs
        runs_folder_name = "runs"
        runs_folder_path = os.path.join(dest_folder_path, runs_folder_name)
        files_aux.makeFolderWithPath(runs_folder_path)

        ##########
        # logger.debug("Phase 1")
        # PHASE 1: STD run
        if communicator is not None:
            communicator.set_total_progress_messages(100)
        std_run_name = "std_run.csv"
        std_run_path = os.path.join(runs_folder_path, std_run_name)
        if communicator is not None:
            communicator.update_completed(1)
        std_run_results = self.compiled_model.simulate(std_run_path)
        if communicator is not None:
            communicator.update_completed(1)

        ##########
        # logger.debug("Phase 2")
        # PHASE 2: Change the values of the parameters that will be fixed throughout all the runs
        # self.fixed_params = list(self.fixed_params)
        if communicator is not None:
            communicator.set_total_progress_messages(100)
        for perturbed_param_info in self.fixed_params:
            # communicator.update_completed(10)
            param_name = perturbed_param_info.name
            new_val = perturbed_param_info.new_val
            # Change the value in the model
            self.compiled_model.setParameterStartValue(param_name, new_val)

        # Make dir for perturbed runs
        perturbed_runs_folder_name = "perturbed"
        perturbed_runs_folder_path = os.path.join(runs_folder_path, perturbed_runs_folder_name)
        files_aux.makeFolderWithPath(perturbed_runs_folder_path)

        ##########
        # PHASE 3: Execute simulations
        # logger.debug("Phase 3")
        sweep_iterations = []
        perturbed_params_info = list(self.runsPerturbedParameters(communicator))
        if communicator is not None:
            communicator.set_total_progress_messages(len(perturbed_params_info)+1)
        perturbed_param_run_id_map = {}
        for i in range(len(perturbed_params_info)):

            # Finished +1 perturbed parameter
            if communicator is not None:
                communicator.update_completed(1)

            # Simulation
            perturbed_param_run_id_str = ""
            swept_params_info = perturbed_params_info[i]
            # Perturb the parameters for this iteration
            for perturbed_param_info in swept_params_info:

                logger.debug("new perturbation")
                logger.debug(perturbed_param_info)

                # Update parameter perturbation
                # Disaggregate param info
                param_name = perturbed_param_info.name
                new_val = perturbed_param_info.new_val
                # Change the value in the model
                self.compiled_model.setParameterStartValue(param_name, new_val)
                # Append new value and enw name
                perturbed_param_run_id_str += param_name + ":" + str(round(new_val, 3)) + ","
            perturbed_param_run_id_str = perturbed_param_run_id_str[:-1]
            perturbed_param_run_id_map[perturbed_param_run_id_str] = i
            # Run the simulation
            simu_csv_name = "run_{0}.csv".format(i)
            simu_csv_path = os.path.join(perturbed_runs_folder_path, simu_csv_name)
            simu_results = self.compiled_model.simulate(simu_csv_path, simu_flags)
            # Instantiate sweep iteration results
            sweep_iter_results = SweepIterationResults(simu_results, swept_params_info)
            # Add results to list
            sweep_iterations.append(sweep_iter_results)
        ##########
        # PHASE 4: Finih
        # Instantiate sweep results
        swept_params_names = [x["name"] for x in self.perturbation_info_per_param]
        sweep_results = ParametersSweepResults(self.model_name,
                                               swept_params_names,
                                               self.fixed_params,
                                               std_run_results,
                                               sweep_iterations, )
        return sweep_results, perturbed_param_run_id_map

    def valuesPerParameter(self):
        return self.sweep_values_per_param

    def runsPerturbedParameters(self, communicator=None):

        # Get the cartesian product of all possible values
        cart_prod_dict = dict_product(self.sweep_values_per_param)

        # Iterate all the combinations instantiating the "PerturbedParameterInfo" objects
        perturbed_parameters_infos = []
        cart_prod_dict = list(cart_prod_dict)
        if communicator is not None:
            communicator.set_total_progress_messages(len(cart_prod_dict) + 1)
        for vals_comb in cart_prod_dict:
            if communicator is not None:
                communicator.update_completed(1)
            run_perturbed_params = []
            for param_name in vals_comb:
                param_default_val = self.params_defaults[param_name]
                param_perturbed_val = vals_comb[param_name]
                perturbed_param_info = simu_run_info.PerturbedParameterInfo(param_name, param_default_val,
                                                                            param_perturbed_val)
                run_perturbed_params.append(perturbed_param_info)
            # Before adding this run, check if all params have been perturbed and it's not the std run
            param_is_default_list = [p.default_val == p.new_val for p in run_perturbed_params]
            if not all(param_is_default_list):
                # If at least one parameter has been perturbed, add it to the list
                perturbed_parameters_infos.append(run_perturbed_params)
        return perturbed_parameters_infos

    # Auxs
    def defaultValuesForParamsToPerturb(self, compiled_model):
        logger.debug(self.perturbation_info_per_param)
        logger.debug(self.fixed_params_raw)
        # Get list of sweep perturbation params
        sweep_params_to_perturb = [ x["name"] for x in self.perturbation_info_per_param ]
        # Get list of fixed perturbation params
        fixed_params_to_perturb = [ x["name"] for x in self.fixed_params_raw ]
        # Join fixed and sweep perturbation params
        params_to_perturb = sweep_params_to_perturb + fixed_params_to_perturb
        # Using the compiled model, ask for the default value of each one
        params_defaults = {}
        logger.debug('parameters to perturb')
        logger.debug(params_to_perturb)
        for p in params_to_perturb:
            logger.debug("###")
            logger.debug(p)

            p_def_val = compiled_model.defaultParameterValue(p)

            logger.debug("===>")
            logger.debug(p_def_val)
            logger.debug(p)
            logger.debug(params_defaults)
            params_defaults[p] = p_def_val
            logger.debug(params_defaults)
        logger.debug("base 3")
        return params_defaults


# Aux
def perturbationInfoForFixedParams(params_defaults, fixed_params_raw):
    fixed_params = []
    # Iterate all the combinations instantiating the "PerturbedParameterInfo" objects
    for fixed_param_pert_dict in fixed_params_raw:
        #Disaggregate fixed param perturbation info
        param_name = fixed_param_pert_dict["name"]
        param_perturbed_val    = fixed_param_pert_dict["value"]
        # Get default val
        param_default_val = params_defaults[param_name]
        # Initialize perturbation info object
        perturbed_param_info = simu_run_info.PerturbedParameterInfo(param_name, param_default_val,
                                                                    param_perturbed_val)
        fixed_params.append(perturbed_param_info)
    return fixed_params


def sweepValuesPerParamFromParamsInfos(params_defaults, perturbation_info_per_param):
    values_per_param = {}
    for p_info in perturbation_info_per_param:
        # Disaggregate param info
        param_name = p_info["name"]
        delta = p_info["delta_percentage"]
        iterations = p_info["iterations"]
        def_value = params_defaults[param_name]
        param_values = valuesForDeltaItersAndDefaultVal(delta, iterations, def_value)
        values_per_param[param_name] = param_values
    return values_per_param


def valuesForDeltaItersAndDefaultVal(perc_perturb, n_iters, def_val):
    # Get limits
    left_limit = def_val * (1 - perc_perturb / 100)
    right_limit = def_val * (1 + perc_perturb / 100)
    # Get middle values (not on borders)
    n_middle_values = n_iters - 2
    limits_distance = right_limit - left_limit
    iterations_delta = limits_distance / (n_middle_values + 1)
    middle_values = [left_limit + iterations_delta * i for i in range(1, n_middle_values + 1)]
    # Return limits and middle values
    values = [left_limit] + middle_values + [right_limit]
    return values


def dict_product(dict_of_lists):
    return (dict(zip(dict_of_lists, x)) for x in itertools.product(*dict_of_lists.values()))


class ParametersSweepResults():
    def __init__(self, model_name, swept_parameters, fixed_parameters, std_run, perturbed_runs):
        self.model_name = model_name
        self.swept_parameters_names = swept_parameters
        self.fixed_parameters_info = fixed_parameters
        self.std_run = std_run
        self.perturbed_runs = perturbed_runs


class SweepIterationResults():
    def __init__(self, simulation_results, swept_params_info):
        self.simulation_results = simulation_results
        self.swept_params_info = swept_params_info
