import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
from statsmodels.tsa.seasonal import seasonal_decompose


def aggregate_transactions(df):
    """
    Aggregate raw transactions into daily transactions for kiosks and products
    and then apply seasonal decomposition to the aggregates.
    
    :param dataframe df: raw item purchased data
    :return dictionary kiosk_result, product_result: result seasonal decomposition
    """

    # Identify all unique kiosks and products, 
    # and then prepare the template dataframes
    unique_kiosk_id = df.kiosk_id.unique()
    daily_kiosk_df = pd.DataFrame(index=unique_kiosk_id)
    unique_product_id = df.product_id.unique()
    daily_product_df = pd.DataFrame(index=unique_product_id)

    # Aggreate number of daily transactions by kiosks and by products
    # in template dataframes
    current = start_date
    delta = relativedelta(days=+1)
    while current <= end_date + delta:
        current_kiosk_df = df[(df.naive_date_time >= current) & \
                            (df.naive_date_time < current + delta)] \
                            .groupby("kiosk_id")["kiosk_id"].agg(np.size)
        current_kiosk_df.name = current
        daily_kiosk_df = daily_kiosk_df.join(current_kiosk_df)
        current_product_df = df[(df.naive_date_time >= current) & \
                            (df.naive_date_time < current + delta)] \
                            .groupby("product_id")["product_id"].agg(np.size)
        current_product_df.name = current
        daily_product_df = daily_product_df.join(current_product_df)
        current += delta

    # Transpose dataframe and fill all N/A with 0
    daily_kiosk_df = daily_kiosk_df.T.fillna(0)
    daily_product_df = daily_product_df.T.fillna(0)

    # Decompose Daily Transactions into Trend, Seasonal, and Residual
    kiosk_result = {}
    for kiosk_id in unique_kiosk_id:
        kiosk_sd = seasonal_decompose(daily_kiosk_df[kiosk_id], \
                    model='additive', two_sided=False)
        kiosk_result[kiosk_id] = kiosk_sd

    product_result = {}
    for product_id in unique_product_id:
        product_sd = seasonal_decompose(daily_product_df[product_id], \
                    model='additive', two_sided=False)
        product_result[product_id] = product_sd
    
    return kiosk_result, product_result


def detect_anomaly(sd_result):
    """
    Use the residuals from the seasonal decomposition result to detect anomaly events.
    (Any residual that is 2 standard devations below the mean)

    :param dataframe sd_result: individual seasonal decomposition result
    :return Pandas DateTimeIndex: date and time of the anomaly events 
    """
    anomaly_date = sd_result.resid[sd_result.resid <= \
                    sd_result.resid.mean() - sd_result.resid.std() * 2]
    return anomaly_date.index


if __name__ == "__main__":

    print("Loading Raw Items Purchased Data")
    df = pd.read_csv("./data/items_purchased.csv")
    if len(df) < 2:
        print("Need at least two samples for the pipeline to work!")
        print("(although it's preferrable to have many more.) Exiting...")
    else:
        # Convert datetime column to naive datetime
        df['naive_date_time'] = pd.to_datetime(df['date_time'].astype(str).str[:-3])

        start_date = df["naive_date_time"].min()
        end_date = df["naive_date_time"].max()
        print("Processing Samples from %s to %s" % (start_date, end_date))

        kiosk_result, product_result = aggregate_transactions(df)

        while True:
            print("\nEnter Ctrl+C to exit")
            print("Do you want detect kiosk anomaly or product anomaly?")
            print("Enter kiosk or product:")
            anomaly_kind = input()
            if anomaly_kind.lower() == "kiosk":
                print("Enter the kiosk ID you want to analyze:")
                kiosk_id = input()
                if kiosk_id.isnumeric():
                    kiosk_id = int(kiosk_id)
                    if kiosk_id in kiosk_result:
                        sd = kiosk_result[kiosk_id]
                        print("Kiosk " + str(kiosk_id) + " Anomaly Events: ")
                        [print(t) for t in detect_anomaly(sd)]
                        print("Close plot to continue.")
                        sd.plot()
                        plt.show()
                    else:
                        print("Kiosk ID not found.")
                else:
                    print("Enter only integers for kiosk ID.")
            elif anomaly_kind.lower() == "product":
                print("Enter the kiosk ID you want to analyze:")
                product_id = input()
                if product_id.isnumeric():
                    product_id = int(product_id)
                    if product_id in product_result:
                        sd = product_result[product_id]
                        print("Product " + str(product_id) + " Anomaly Events: ")
                        [print(t) for t in detect_anomaly(sd)]
                        print("Close plot to continue.")
                        sd.plot()
                        plt.show()
                    else:
                        print("Product ID not found.")
                else:
                    print("Enter only integers for product ID.")
            else:
                print("Please enter the correct selection.")
