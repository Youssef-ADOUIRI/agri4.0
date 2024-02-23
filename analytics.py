import streamlit as st
import pandas as pd
import altair as alt

temperature_data = pd.read_csv("temperature_forecast_lstm.csv", delimiter=",")
humidity_data = pd.read_csv("humidity_forecast.csv", delimiter=",")
locations = pd.read_csv("locations.csv", delimiter=",")
stations = locations["Station"].tolist()

# Page configuration
st.set_page_config(
    page_title="Temperature and Humidity Dashboard", page_icon="🌡️", layout="wide"
)

# Sidebar
st.sidebar.title("Dashboard Options")

# Main content
st.title("Temperature and Humidity Dashboard")

# Sidebar options
selected_data = st.sidebar.radio("Select a data type", ["Temperature", "Humidity"])

selected_station = st.sidebar.selectbox("Select a station", stations)

station_data_isfound = True

# Select the appropriate dataset based on user choice
if selected_data == "Temperature":
    selected_data_notation = selected_data
    selected_date_notation = "Date"
    chart_title = "Temperature Charts"
    y_axis_label = "Temperature (°C)"
    preselected_dataset = temperature_data
    if selected_station + selected_data_notation not in preselected_dataset.columns:
        station_data_isfound = False

else:
    selected_data_notation = " Relative Humidity"
    selected_date_notation = " Date"
    chart_title = "Humidity Charts"
    y_axis_label = "Humidity (%)"
    preselected_dataset = humidity_data
    if selected_station + selected_data_notation not in preselected_dataset.columns:
        station_data_isfound = False


if station_data_isfound:
    selected_dataset = preselected_dataset[
        [
            selected_station + selected_date_notation,
            selected_station + selected_data_notation,
        ]
    ]
    selected_dataset[selected_station + selected_date_notation] = pd.to_datetime(
        selected_dataset[selected_station + selected_date_notation]
    )
    # Line chart with Altair
    line_chart = (
        alt.Chart(selected_dataset)
        .mark_line(point=True)
        .encode(
            x=alt.X(selected_station + selected_date_notation + ":T", title="Date"),
            y=alt.Y(
                f"{selected_station + selected_data_notation}:Q", title=y_axis_label
            ),
            tooltip=[
                selected_station + selected_date_notation + ":T",
                f"{selected_station + selected_data_notation}:Q",
            ],
        )
        .interactive()
    )
    st.subheader(f"{selected_data} for the next week")
    st.altair_chart(line_chart, use_container_width=True)
    daily_weather = (
        selected_dataset.groupby(
            selected_dataset[selected_station + selected_date_notation].dt.date
        )
        .agg({selected_station + selected_data_notation: ["mean", "min", "max"]})
        .reset_index()
    )
    # Rename the columns
    daily_weather.columns = ["Date", "Daily Average", "Min", "Max"]
    # Round the data column
    daily_weather["Daily Average"] = daily_weather["Daily Average"].round(0)
    daily_weather["Min"] = daily_weather["Min"].round(0)
    daily_weather["Max"] = daily_weather["Max"].round(0)

    # Replace dates with weekday names
    daily_weather["Date Raw"] = pd.to_datetime(daily_weather["Date"])
    daily_weather["Date"] = daily_weather["Date Raw"].dt.strftime("%A")
    # Rename column headers

    st.title("Weather :")
    # Display the weather data
    st.write(f"Daily Average, Minimum, and Maximum {selected_data}:")
    st.dataframe(daily_weather[["Date", "Daily Average", "Min", "Max"]], width=800)

    # Add functionality to click on the date to plot temperature for that day
    selected_date = st.selectbox(
        "Select a date:", daily_weather["Date Raw"].dt.date.unique()
    )
    # Filter the data for the selected date
    selected_day_data = selected_dataset[
        selected_dataset[selected_station + selected_date_notation].dt.date
        == selected_date
    ]

    # Plot the temperature for the selected day
    if not selected_day_data.empty:
        chart = (
            alt.Chart(selected_day_data)
            .mark_line(point=True)
            .encode(
                x=alt.X(selected_station + selected_date_notation + ":T", title="Date"),
                y=alt.Y(
                    f"{selected_station + selected_data_notation}:Q", title=y_axis_label
                ),
            )
            .properties(
                width=600, height=400, title=f"{selected_data} for {selected_date}"
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No data available for the selected date.")

else:
    st.markdown(
        f'<p style="color:#ff0000;font-size:24px;text-align:center;">The {selected_station} station do not have enough {selected_data} data for the next week</p>',
        unsafe_allow_html=True,
    )
