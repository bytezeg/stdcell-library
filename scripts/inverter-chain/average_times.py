from PyLTSpice.LTSpice_RawRead import RawRead as RawRead
import numpy as np


def print_array_size(arr):
    """
    Print the size of a numpy array along with its name or "Variable" if the name cannot be determined.
    :param arr: (numpy.ndarray): The numpy array to print the size of.
    :return: Integer
    """
    for key, value in globals().items():
        if value is arr:
            var_name = key
            break
    else:
        var_name = "Variable"

    print(f'\n>>> Size of "{var_name}" : {arr.size}')
    return arr.size


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
    :return: vector with rise times and fall times for specific corner
    """
    rise_time_values = corner.get_trace('trv').get_wave(0)  # returns a np array
    fall_time_values = corner.get_trace('tfv').get_wave(0)  # returns a np array
    return [rise_time_values, fall_time_values]  # return both arrays at the same time


# Read the data from each corner
tt = RawRead("data_rs_tt.raw")
sf = RawRead("data_rs_sf.raw")
ff = RawRead("data_rs_ff.raw")
ss = RawRead("data_rs_ss.raw")
fs = RawRead("data_rs_fs.raw")
ll = RawRead("data_rs_ll.raw")
hh = RawRead("data_rs_hh.raw")
hl = RawRead("data_rs_hl.raw")
lh = RawRead("data_rs_lh.raw")

# Group all corner data into a np array
corners = np.array([tt, sf, ff, ss, fs, ll, hh, hl, lh])
wn_values = tt.get_trace('wnv').get_wave(0)  # Getting wn values to plot
tt_rt_values = corner_values(corners[0])[0]  # All rise times values from tt simulation.

print_array_size(corners)
print_array_size(wn_values)
iterations = print_array_size(tt_rt_values)

# Grouping timing data from all corners into matrices
rt_values = np.array([])  # each element of this array (a corner) is also an array of 143 elements (a time)
ft_values = np.array([])  # each element of this array (a corner) is also an array of 143 elements (a time)
for i in range(corners.size):
    rt_values = np.append(rt_values, corner_values(corners[i])[0])  # matrix of rise-times
    ft_values = np.append(ft_values, corner_values(corners[i])[1])  # matrix of fall-times

# Reshaping
print_array_shape(rt_values)
rt_values = np.reshape(rt_values, (
    corners.shape[0], wn_values.size))  # reshape rt_values: rows -> corners, columns -> total w iterations
ft_values = np.reshape(ft_values, (
    corners.shape[0], wn_values.size))  # reshape ft_values: 18 files (18 corners) and 143 columns (143 iterations of W)
print_array_shape(rt_values)
rt_values = rt_values.T
ft_values = ft_values.T
print_array_shape(rt_values)
print_array_shape(ft_values)

# Method 1

# Average per (Wn,Wp) across all corners
rt_averages = np.array([])
ft_averages = np.array([])
for w in range(wn_values.size):
    rt_averages = np.append(rt_averages, rt_values[w, :].mean())
    ft_averages = np.append(ft_averages, ft_values[w, :].mean())

# Average of averages
print_array_size(rt_averages)  # should be 143 because we have 143 (Wn, Wp)
final_rt_averages = rt_averages.mean()
final_ft_averages = ft_averages.mean()
average_1 = (final_rt_averages + final_ft_averages) / 2

print('\n>>>> Average 1: ', average_1)

# Method 2

rt_final = np.sum(rt_values)
ft_final = np.sum(ft_values)
average_2 = (rt_final + ft_final) / (2 * wn_values.size * corners.size)

print('>>>> Average 2: ', average_2)

# Method 3

average_3 = np.mean(rt_values + ft_values) / 2
print('>>>> Average 3: ', average_3)
