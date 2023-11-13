#!/usr/bin/env python
# coding: utf-8

# # $\Phi$-SO demo (quick SR)

# In[1]:
import os
import mlflow
import mlflow.pyfunc
from mlflow import log_metric, log_param, log_artifact, log_text

# External packages
import numpy as np
import matplotlib.pyplot as plt
# Internal code import
    
import subprocess
import argparse
import pandas as pd
import csv
import ast
from PIL import Image
# using resource 
import resource
  
def limit_memory(maxsize):
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (maxsize, hard))

parser = argparse.ArgumentParser(description='parser')
parser.add_argument('--data', type=str, help='csv path', default = "/user/mahaohui/autoML/PhySO/demo/demo_mechanical_energy/mechanical.csv")
args = parser.parse_args()

# Guard for spawn systems (typically MACs/Windows)
if __name__ == '__main__':

    # limit cpu memory usage as 4g
    limit_memory(1024*1024*1024*20)

    # texlive_path = os.path.join(__file__.split("demo")[0],"latex")
    texlive_path = "/user/mahaohui/autoML/PhySO/latex"
    print("texlive_path:",texlive_path)
    os.system(f"export MANPATH={texlive_path}/texlive/2023/texmf-dist/doc/man:$MANPATH")
    os.system(f"export INFOPATH={texlive_path}/texlive/2023/texmf-dist/doc/info:$INFOPATH")
    os.system(f"export PATH={texlive_path}/texlive/2023/bin/x86_64-linux:$PATH")

    # In[2]:
    X_names = []
    X_units = []
    X_values = []
    fixed_consts = []
    fixed_consts_units = []
    free_consts_names = []
    free_consts_units = []
    
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    external_csv_path = os.path.join(parent_dir,'data',args.data)
    if os.path.exists(external_csv_path):
        df = pd.read_csv(external_csv_path)
    else:
        df = pd.read_csv(args.data)
    for column in df.columns:
        if "x_name" in column:
            X_names.append(column.split(":")[1])
            X_unit = ast.literal_eval(df[column][0])
            X_units.append(X_unit)
            X_value = np.array(df[column][1:])
            X_values.append([float(i) for i in X_value]) 
        elif "y_name" in column:
            y_name=column.split(":")[1]
            y_units = ast.literal_eval(df[column][0])
            y_value = np.array(df[column][1:])
            y=[float(i) for i in y_value]
        elif "fix_const" in column:
            fixed_consts.append(float(df[column][1]))
            fixed_consts_units.append(ast.literal_eval(df[column][0]))
        elif "free_const" in column:
            free_consts_names.append(column.split(":")[1])
            free_consts_units.append(ast.literal_eval(df[column][0]))
            
    X = np.stack([i for i in X_values], axis=0)
    
    print("X_units:",X_units)
    print("y_unit:",y_units)
    print("fixed_consts",fixed_consts)
    print("fixed_consts_units",fixed_consts_units)
    print("free_consts_names",free_consts_names)
    print("free_consts_units",free_consts_units)
    # exit()


    # Where $X=(z,v)$, $z$ being a length of dimension $L^{1}, T^{0}, M^{0}$, v a velocity of dimension $L^{1}, T^{-1}, M^{0}$, $y=E$ if an energy of dimension $L^{2}, T^{-2}, M^{1}$.
    #
    # It be noted that free constants search starts around 1. by default. Therefore when using default hyperparameters, normalizing the data around an order of magnitude of 1 is strongly recommended.

    # Dataset plot

    # In[3]:


    # n_dim = X.shape[0]
    # fig, ax = plt.subplots(n_dim, 1, figsize=(10,5))
    # for i in range (n_dim):
    #     curr_ax = ax if n_dim==1 else ax[i]
    #     curr_ax.plot(X[i], y, 'k.',) # type: ignore
    #     curr_ax.set_xlabel("X[%i]"%(i)) # type: ignore
    #     curr_ax.set_ylabel("y") # type: ignore
    # plt.show()


    # ### Running SR task

    # #### Available configurations

    # It should be noted that SR capabilities of `physo` are heavily dependent on hyperparameters, it is therefore recommended to tune hyperparameters to your own specific problem for doing science.
    # Summary of available currently configurations:
    #
    # |  Config |                           Notes                           |
    # |:-------:|:---------------------------------------------------------:|
    # | config0 | Light config for demo purposes.                           |
    # | config1 | Tuned on a few physical cases.                            |
    # | config2 | [work in progress] Good starting point for doing science. |
    #
    # By default, `config0` is used, however it is recommended to use the latest configuration currently available (`config1`) as a starting point for doing science.
    #

    # #### Running physo

    # Given the units input variables $(x_0,..., x_n)$ (here $(z, v)$ ), the root variable $y$ (here $E$) as well as free and fixed constants, you can run an SR task to recover $f$ via:

    # (Allowing the use of a fixed constant $1$ of dimension $L^{0}, T^{0}, M^{0}$ (ie dimensionless) and free constants $m$ of dimension $L^{0}, T^{0}, M^{1}$ and $g$ of dimension $L^{1}, T^{-2}, M^{0}$.)
    #
    # It should be noted that here the units vector are of size 3 (eg: `[1, 0, 0]`) as in this example the variables have units dependent on length, time and mass only.
    # However, units vectors can be of any size $\leq 7$ as long as it is consistent across X, y and constants, allowing the user to express any units (dependent on length, time, mass, temperature, electric current, amount of light, or amount of matter).
    # In addition, dimensional analysis can be performed regardless of the order in which units are given, allowing the user to use any convention ([length, mass, time] or [mass, time, length] etc.) as long as it is consistent across X,y and constants.
    
    # In[4]:
    import physo
    with mlflow.start_run() as run:
        # mlflow.log_figure(fig, "image.png")
        print("physo.config.config0.config0", physo.config.config0.config0)

        # Running SR task
        expression, logs = physo.SR(X, y,
                                    # Giving names of variables (for display purposes)
                                    X_names = X_names,
                                    # Giving units of input variables
                                    X_units = X_units,
                                    # Giving name of root variable (for display purposes)
                                    y_name  = y_name,
                                    # Giving units of the root variable
                                    y_units = y_units,
                                    # Fixed constants
                                    fixed_consts = fixed_consts,
                                    # Units of fixed constants
                                    fixed_consts_units = fixed_consts_units,
                                    # Free constants names (for display purposes)
                                    free_consts_names = free_consts_names,
                                    # Units offFree constants
                                    free_consts_units = free_consts_units,
                                    # Run config
                                    run_config = physo.config.config0.config0,
        )

        # ### Inspecting the best expression found

        # In[5]:

        # Inspecting the best expression found
        # In ascii
        print("\nIn ascii:")
        print(expression.get_infix_pretty(do_simplify=True))
        mlflow.log_text( expression.get_infix_pretty(do_simplify=True),"In_ascii_info")
        # In latex
        print("\nIn latex")
        print(expression.get_infix_latex(do_simplify=True))
        mlflow.log_text( expression.get_infix_latex(do_simplify=True),"\nIn latex")
        # Free constants values
        print("\nFree constants values")
        print(expression.free_const_values.cpu().detach().numpy())
        # mlflow.log_metric("Free_constants_values", expression.free_const_values.cpu().detach().numpy())
        
        # mlflow.log_metric("args_test_data:",args.test_data)

        # ### Inspecting pareto front expressions

        # In[6]:

        # Inspecting pareto front expressions
        pareto_front_complexities, pareto_front_expressions, pareto_front_r, pareto_front_rmse = logs.get_pareto_front()
        for i, prog in enumerate(pareto_front_expressions):
            str = ""
            str += prog.get_infix_pretty(do_simplify=True)+"\n"
            # Showing expression
            print(prog.get_infix_pretty(do_simplify=True))
            # Showing free constant
            free_consts = prog.free_const_values.detach().cpu().numpy()
            for j in range (len(free_consts)):
                print("%s = %f"%(prog.library.free_const_names[j], free_consts[j]))
                str += "!!!%s = %f"%(prog.library.free_const_names[j], free_consts[j])+"\n"
            # Showing RMSE
            print("RMSE = {:e}".format(pareto_front_rmse[i]))
            str += "RMSE = {:e}".format(pareto_front_rmse[i])+"\n"
            print("-------------\n")
            str += "-------------\n"+"\n"
            mlflow.log_text(str, f"pareto_front_expressions {i}")
        
        img_PIL = Image.open("SR_curves.png")
        # mlflow.log_metric()
        # mlflow.log_image(img_PIL, "SR_curves.png")
        
        output_df = pd.read_csv("SR_curves_pareto.csv")
        for i in output_df.index:
            for j in output_df.columns:
                mlflow.log_metric(f"expression_{i}:",output_df[j].iloc[i])
        
        # mlflow.log_table(data=df, artifact_file="SR_curves_pareto.csv")

        # In[ ]:
        mlflow.end_run()
