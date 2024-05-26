import xgboost as xgb
from joblib import load
import pandas as pd
import numpy as np
import time
import warnings
from pandas.errors import SettingWithCopyWarning
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt


warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

def convert_string_to_seconds(time_str):
    """
    Converts a time string to the total number of seconds.
    
    Parameters:
    time_str (str): The time string to be converted. It should be in the format 'HH:MM:SS' or 'HH:MM'.
    
    Returns:
    int: The total number of seconds represented by the time string.
    """
    try:
        # Try to convert the time string to datetime format with seconds
        date_time_value = pd.to_datetime(time_str, format='%H:%M:%S')
        total_seconds = date_time_value.hour * 3600 + date_time_value.minute * 60 + date_time_value.second
    
    except:
        # If the conversion fails, try to convert the time string to datetime format without seconds
        date_time_value = pd.to_datetime(time_str, format='%H:%M')
        total_seconds = date_time_value.hour * 3600 + date_time_value.minute * 60 + date_time_value.second
        
    return total_seconds

# Function to convert seconds to a time string
def convert_seconds_to_string(seconds, output_seconds= False):
    """
    Converts the given number of seconds into a string representation of time in the format HH:MM:SS.

    Parameters:
    seconds (int): The number of seconds to convert.

    Returns:
    str: The string representation of time in the format HH:MM:SS.
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if output_seconds == False:
        return "{:02d}:{:02d}".format(int(hours), int(minutes))
    
    else:
        return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

print("\n>> loading regression models")
booster = xgb.Booster()

try:
    knn = load('regression_model/models/knn_regressor.joblib')
    rf = load('regression_model/models/random_forest_8_trees.joblib')
    booster.load_model('regression_model/models/xgboost_model.json')
    tpl_encoder = load('regression_model/train_station_encoder_model.sav')
except:
    knn = load('models/knn_regressor.joblib')
    rf = load('models/random_forest_8_trees.joblib')
    booster.load_model('models/xgboost_model.json')
    tpl_encoder = load('train_station_encoder_model.sav')



print(">> Regression models loaded\n")


def plot_clf_scores(data, _true_value= None, show=False):
    models = data['models']
    predicted_values = data['predictions']
    true_value = _true_value

    plt.figure(figsize=(13, 5))
    plt.scatter(predicted_values, models)
    plt.axvline(x=true_value, color='r', linestyle='--')  # Add a vertical red line at the true value
    plt.xlabel('Predicted Values')
    plt.ylabel('Models')
    plt.title('Scatter plot of Models vs Predicted Values')
    plt.savefig(f'plots/Comparison/Scatter plot of Models vs Predicted Value {true_value}.jpeg')
    if show != False:
        plt.show()
    else:
        pass
    plt.close()

def make_delay_prediction(input: pd.DataFrame, output_type=int, debug=False, plot_scores=False, true_value=False):
    """
    Predicts the delay based on the input data using multiple regression models.
    This function will also handle the string to int conversion and also the 
    string to tpl encoded values. You MUST give it the short tpl string for
    the encoder to work eg.'London Liverpoost Street' -> 'LIVST'
    
    Parameters:
    input (array-like): The input data for prediction.
    
        ********************************************************************************
        ** The input array must be similar to this format:                            **
        **                                                                            **
        ** |____tpl_____|___depart_from_LDN_____|___depart_from_current_station_____| **
        ** |17 or "DISS"|   10392 or "12:40"    |        10812 or "13:15"           | **
        **                                                                            **
        ********************************************************************************
    
    
    output_type (int or str): Changes the output value to be either str (string) eg. "12:53"
    or int (integer) eg. 241523. This will default to int.
    
    Returns:
    float: The predicted delay in seconds from midnight.
    or 
    string: The predicted delay in 24hr format.
    """
    if debug == True:
        start_time = time.time()
    else:
        pass
    
    # will check if the time values of the input df are pre-converted, if so it will convert 
    # the values
    if input['depart_from_LDN'].dtype == 'O':
        input['depart_from_LDN'] = convert_string_to_seconds(input['depart_from_LDN'][0])
    else:
        pass
    if input['depart_from_current_station'].dtype == 'O':
        input['depart_from_current_station'] = convert_string_to_seconds(input['depart_from_current_station'][0])
    else:
        pass
    if input['tpl'].dtype == 'O':
        input['tpl'] = tpl_encoder.transform(input['tpl'])
    else:
        pass
    
    # Makes the prediction using XGBoost, KNN regression, Random Forest regression.
    test_data = xgb.DMatrix(input)
    xgb_pred = booster.predict(test_data)
    knn_pred = knn.predict(input)
    rf_pred = rf.predict(input)
    # Collects average score
    average_all = (xgb_pred[0] + knn_pred[0] + rf_pred[0]) / 3
    
    if plot_scores and true_value is not None:
        true_value = convert_string_to_seconds(true_value[0])
    if plot_scores != False:
        data = pd.DataFrame({'models' : ['XGBoost', 'KNN', 'Random Forest', 'Average'],
                'predictions' : [xgb_pred, knn_pred, rf_pred, average_all]})
        plot_clf_scores(data, _true_value = true_value)
    else:
        pass
    
    # Checks what the output format should be
    if output_type == str:
        average_all = convert_seconds_to_string(average_all)
        
    elif output_type == pd.DataFrame:
        average_all = pd.DataFrame({average_all})
    else:
        pass
        
    if debug == True:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time} seconds")
    else:
        pass
    
    return average_all

def score_model(data):
    """
    Calculates and prints the root mean squared error (RMSE) and mean absolute error (MAE) 
    for a regression model's predictions.

    Parameters:
    data (pandas.DataFrame): The input data containing the features used for prediction.

    Returns:
    None
    """

    y_value = pd.DataFrame({convert_string_to_seconds(data['arrive_at_NRW'][0])})
    ŷ_pred = make_delay_prediction(data[['tpl','depart_from_LDN', 'depart_from_current_station']], output_type=pd.DataFrame,)
    
    mse = mean_squared_error(y_value, ŷ_pred)
    # rmse = np.sqrt(mean_squared_error(y_value, ŷ_pred)) 
    mae = mean_absolute_error(y_value, ŷ_pred)

    print('The lower the score the better!')
    print("MSE : % f" %(mse))
    # print("RMSE : % f" %(rmse))
    print("MAE : % f" %(mae))
    print(f"MAE in time: {(convert_seconds_to_string(int(mae)))}")

    

    print('-' * 30)

if __name__ == "__main__":
    # Creating a dict with the data for a use case of leaving ipswich at 12:53
    _example_data = {"tpl" : ["IPSWICH"],
                    "depart_from_LDN": ["12:00"],
                    "depart_from_current_station" : ["12:53"]}

    example_data = pd.DataFrame(_example_data)


    print(f"Input: {_example_data}\n")
    print(f"Output: {make_delay_prediction(example_data)}\n\n")