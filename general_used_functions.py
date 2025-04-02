
import os
import json
import numpy as np
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from hmmlearn import hmm
import joblib


def load_config_file():
    # Open the config file
    config_file_path = os.path.join(os.getcwd(), 'config.json')
    with open(config_file_path) as f:
        config = json.load(f)

    return config


def check_weird_data(data):
    """
    Check if data contains NaN, inf, or -inf
    :param data: DataFrame
    """
    if data.isnull().values.any() or data.isin([np.inf, -np.inf]).values.any():
        return True
    return False


# Handle unmatched date format
def parse_dates(date_series):
    return pd.to_datetime(date_series, dayfirst=False)


def load_training_data():
    config_data = load_config_file()

    # Load training data
    DATA_DIR = os.getcwd() + '/data'
    training_stock_df = defaultdict(list)
    stock_list = config_data['stock_dict'].keys()

    for stock in stock_list:
        feature_data = pd.read_excel(
            f'{DATA_DIR}/training_data_full/training_feature_{stock}.xlsx')
        stock_data = pd.read_excel(
            f'{DATA_DIR}/stock_price_data/training/{stock}_stock_price_data(training).xlsx')

        # Merge the two dataframes on 'date'
        merged_data = pd.merge(feature_data, stock_data, on='date', how='left')

        # # Drop the 'date' column from the feature data
        # merged_data.drop(columns=['date'], inplace=True)

        # Store the merged data in the dictionary
        training_stock_df[stock] = merged_data

    return training_stock_df


def plot_train_market_regmie(states, stock):
    sns.set(font_scale=15)
    # Dynamically determine unique states
    unique_states = sorted(states['states'].unique())
    # Generate a color palette with as many colors as unique states
    custom_palette = dict(
        zip(unique_states, sns.color_palette("Set1", n_colors=len(unique_states))))
    sns.set(style="whitegrid")
    fg = sns.FacetGrid(data=states, hue='states',
                       hue_order=unique_states, palette=custom_palette, aspect=1.31, legend_out=False)
    fg.map(plt.scatter, 'Date', stock, alpha=0.8)
    fg.add_legend(prop={'size': 20}, title="States", title_fontsize='20')
    fg.fig.suptitle(
        f'Historical {stock} Market Trend', fontsize=80, fontweight='bold')
    fg.fig.set_size_inches(80, 40)
    sns.despine(offset=10)
    plt.show()


def HMM_training(stock, train_df, n_components=3, n_iter=10 ^ 1000000000000000000000000000000000):
    # Exclude the date column when training the model
    features = train_df.drop(columns=['date'])
    model = hmm.GaussianHMM(n_components=n_components,
                            covariance_type="full", n_iter=n_iter)
    model.fit(features)
    hidden_states = model.predict(features)

    # Build the states DataFrame with only Date, the stock price column, and hidden states.
    states = pd.DataFrame({
        'Date': train_df['date'],
        stock: train_df[stock],
        'states': hidden_states
    })

    plot_train_market_regmie(states, stock)

    return model, states


def save_HMM_states_excel(stock, states):
    # Load training data
    DATA_DIR = os.getcwd() + '/data'

    # If the directory does not exist, create it
    os.makedirs(f"{DATA_DIR}/HMM_states", exist_ok=True)

    states.to_excel(
        f"{DATA_DIR}/HMM_states/{stock}_HMM_states.xlsx", index=False)


def save_HMM_model(stock, model):
    # Define the directory for saving models and create it if it doesn't exist
    DATA_DIR = os.path.join(os.getcwd(), 'model')
    os.makedirs(DATA_DIR, exist_ok=True)

    # Save the model using joblib
    model_filename = os.path.join(DATA_DIR, f'{stock}_HMM_model.joblib')
    joblib.dump(model, model_filename)

# # Training
# for stock, weird_columns in training_weird_columns_dict.items():
#     if weird_columns:
#         training_feature_df[stock] = handle_weird_data_with_knn_imputer(training_feature_df[stock], weird_columns)

# # Testing
# for stock, weird_columns in testing_weird_columns_dict.items():
#     if weird_columns:
#         testing_feature_df[stock] = handle_weird_data_with_knn_imputer(testing_feature_df[stock], weird_columns)

# # Check the data again
# for stock, stock_data in training_feature_df.items():
#     if check_weird_data(stock_data):
#         print(f"The {stock} stock price data still contains weird data in training data")

# for stock, stock_data in testing_feature_df.items():
#     if check_weird_data(stock_data):
#         print(f"The {stock} stock price data still contains weird data in testing data")

# # Clear weird_columns_dict, only clear the value, not the key
# for stock in stock_list:
#     training_weird_columns_dict[stock] = []

# for stock in stock_list:
#     testing_weird_columns_dict[stock] = []

# # Print the result to ensure the data is correct
# print(training_feature_df['AAPL'].head().to_string())
# print(testing_feature_df['AAPL'].head().to_string())
