from fastdtw import fastdtw
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle
import json

subseries_length = 64*1
forecast_length = subseries_length*3 # + (64*5)
thresh = 1.2

def prev_trends(total_series,subseries):
    subseries_length = len(subseries)
    series = total_series[:-subseries_length]
    std_subseries = (subseries - np.mean(subseries)) / np.std(subseries)

    distances = []
    # Slide through the larger series and compute distances
    for i in range(len(series) - subseries_length + 1):
        segment = series[i:i + subseries_length, 1]
        std_segment = (segment - np.mean(segment)) / np.std(segment)
        distance, _ = fastdtw(std_subseries, std_segment)
        distances.append(distance)

    # You may want to find the index of the minimum distance
    max_dist, min_dist = max(distances), min(distances)
    threshold = min_dist * thresh # Plot the original series

    prev_trends = []
    dist_len = len(distances)
    i = 0
    # Iterate through the distances and add to count and store colors if within threshold
    while i < dist_len:
        if distances[i] <= threshold:
            accuracy_rating = (1 - (distances[i] - min_dist) / (max_dist - min_dist)) * 100
            prev_trends.append((i,accuracy_rating))
            i += subseries_length
        else: i += 1

    return prev_trends

def plot_trends(series, subseries, prev_trends):
    colors = cycle(['r', 'b', 'y', 'm', 'c'])
    plt.plot(series[:, 0], series[:, 1], label='Series 2')
    subseries_length = len(subseries)

    for i, accuracy in prev_trends:
        plt.plot(series[i:i+subseries_length, 0], series[i:i+subseries_length, 1], next(colors) + '-', label=f"{accuracy:.2f}% Accuracy")

    plt.plot(series[-subseries_length:, 0], subseries, 'g-', label='Subseries (Series 1)')
    plt.xlabel('Time')
    plt.ylabel('Standardized Value')
    plt.legend()
    plt.show()

def forecast(series, prev_trends):
    forecasts = []
    # forecasts_length = 90
    for i,_ in prev_trends:
        segment = series[i:i+forecast_length, 1]
        std_segment = (segment - np.mean(segment)) / np.std(segment)
        plt.plot(series[:forecast_length, 0], std_segment, label=f"{i}", linestyle='--')
        forecasts.append(std_segment)
    stacked_series = np.stack(forecasts)
    average_series = np.mean(stacked_series, axis=0)
    plt.plot(series[:forecast_length, 0], average_series, label='Average', linewidth=2, color='g')
    plt.axvline(x=series[subseries_length-1, 0], color='r', linestyle='--')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.show()
    return forecasts, average_series

def get_series(filename):
    f = open(filename)
    data = json.load(f)
    candles = data["candles"]

    time = [candle['datetime'] for candle in candles]
    volume = [candle['volume'] for candle in candles]
    close = [candle['close'] for candle in candles]

    time = np.array(time)
    volume = np.array(volume)
    close = np.array(close)
    time = (time - time[0]) / (1000 * 3600 * 24) # Convert from milliseconds to days
    series = np.column_stack((time, close))
    return series

series = get_series("stock_name.json")
subseries = series[-subseries_length:, 1]

past_trends = prev_trends(series,subseries)
plot_trends(series, subseries, past_trends)
forecast(series, past_trends)
