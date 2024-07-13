from PyLTSpice.LTSpice_RawRead import RawRead as RawRead
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString
from sklearn.linear_model import LinearRegression


def print_array_size(arr):
    """
    Print the size of a numpy array along with its name or "Variable" if the name cannot be determined.
    :param arr: (numpy.ndarray): The numpy array to print the size of.
    :return: None
    """
    for key, value in globals().items():
        if value is arr:
            var_name = key
            break
    else:
        var_name = "Variable"

    print(f'\n>>> Size of "{var_name}" : {arr.size}')


def print_array_shape(arr):
    """
    Print the size of a numpy array along with its name or "Variable" if the name cannot be determined.
    :param arr: (numpy.ndarray): The numpy array to print the size of.
    :return: None
    """
    for key, value in globals().items():
        if value is arr:
            var_name = key
            break
    else:
        var_name = "Variable"

    print(f'\n>>> Shape of "{var_name}" : {arr.shape}')


def corner_values(corner):
    """
    This function returns the plottable data of the corner
    :param corner:
    :return: vector with rise time and fall time for specific corner
    """
    rise_time_values = corner.get_trace('trv').get_wave(0)  # returns a np array
    fall_time_values = corner.get_trace('tfv').get_wave(0)  # returns a np array
    return [rise_time_values, fall_time_values]  # return both arrays at the same time


# Read the data from each corner
tt = RawRead("data_tt.raw")
sf = RawRead("data_sf.raw")
ff = RawRead("data_ff.raw")
ss = RawRead("data_ss.raw")
fs = RawRead("data_fs.raw")
ll = RawRead("data_ll.raw")
hh = RawRead("data_hh.raw")
hl = RawRead("data_hl.raw")
lh = RawRead("data_lh.raw")

# Group all corner data into a np array
corners = np.array([tt, sf, ff, ss, fs, ll, hh, hl, lh])
wn_values = tt.get_trace('wnv').get_wave(0)  # Getting wn values to plot
tt_rt_values = corner_values(corners[0])[0]

print_array_size(corners)
print_array_size(wn_values)
print_array_size(tt_rt_values)

# Grouping timing data from all corners into matrices
rt_values = np.array([])  # each element of this array (a corner) is also an array of 143 elements (a time)
ft_values = np.array([])  # each element of this array (a corner) is also an array of 143 elements (a time)
for i in range(corners.size):
    rt_values = np.append(rt_values, corner_values(corners[i])[0])  # matrix of rise-times
    ft_values = np.append(ft_values, corner_values(corners[i])[1])  # matrix of fall-times

# Reshaping
print_array_shape(rt_values)
rt_values = np.reshape(rt_values,
                       (corners.shape[0], wn_values.size))  # reshape rt_values: 18 files (18 corners) and 143 columns (143 iterations of W)
ft_values = np.reshape(ft_values,
                       (corners.shape[0], wn_values.size))  # reshape ft_values: 18 files (18 corners) and 143 columns (143 iterations of W)
print_array_shape(rt_values)
rt_values = rt_values.T
ft_values = ft_values.T
print_array_shape(rt_values)
print_array_shape(ft_values)

# Average per (Wn,Wp) across all corners
rt_averages = np.array([])
ft_averages = np.array([])
for w in range(wn_values.size):
    rt_averages = np.append(rt_averages, rt_values[w, :].mean())
    ft_averages = np.append(ft_averages, ft_values[w, :].mean())

plt.plot(wn_values, ft_averages, label='Fall Time', color='red')
plt.plot(wn_values, rt_averages, label='Rise Time', color='blue')

# Cross
print('Cross point')
first_line = LineString(np.column_stack((wn_values, ft_averages)))
second_line = LineString(np.column_stack((wn_values, rt_averages)))
intersection = first_line.intersection(second_line)
print('The intersection is:', intersection)

plt.xlabel('NMOS Width (Wn) [um]')
plt.ylabel('Time [s]')
plt.title("Rise and Fall Times")
plt.legend()
plt.show()

# Regression

rates = rt_averages / ft_averages
print_array_shape(rates)
print_array_size(rates)

x = wn_values.reshape((-1,1))
y = rates
reg = LinearRegression().fit(x, y)
print(f">>> Reg model: rate = {reg.coef_}Wn + {reg.intercept_}")
yp = reg.coef_ * x + reg.intercept_

plt.plot(x, y, color="red", label="Real")
plt.plot(x, yp, color="blue", label="Predicted")
plt.xlabel('Wn Values')
plt.ylabel('Rates')
plt.legend()
plt.show()

mse = np.sqrt(np.mean(np.square(y - yp)))
min_index = np.argmin(mse)
print(min_index)
print('>>> Optimal Wn: ', x[min_index])


