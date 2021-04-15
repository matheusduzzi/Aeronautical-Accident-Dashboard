# importar bibliotecas
import streamlit as st
import pandas as pd
import pydeck as pdk

DATA_URL = "https://raw.githubusercontent.com/carlosfab/curso_data_science_na_pratica/master/modulo_02/ocorrencias_aviacao.csv"

@st.cache
def load_data():
    """
    """
    columns = {
        'ocorrencia_latitude': 'latitude',
        'ocorrencia_longitude': 'longitude',
        'ocorrencia_dia': 'date',
        'ocorrencia_classificacao': 'classification',
        'ocorrencia_tipo': 'type',
        'ocorrencia_tipo_categoria': 'type_category',
        'ocorrencia_tipo_icao': 'type_icao',
        'ocorrencia_aerodromo': 'aerodrome',
        'ocorrencia_cidade': 'city',
        'investigacao_status': 'status',
        'divulgacao_relatorio_numero': 'report_number',
        'total_aeronaves_envolvidas': 'aircraft_involved'
    }

    data = pd.read_csv(DATA_URL, index_col='codigo_ocorrencia')
    data = data.rename(columns=columns)
    data.date = data.date + " " + data.ocorrencia_horario
    data.date = pd.to_datetime(data.date)
    data = data[list(columns.values())]
    data = data.replace(['INCIDENTE GRAVE','INCIDENTE', 'ACIDENTE'], 
                     ['SERIOUS INCIDENT','INCIDENT','ACCIDENT']) 

    return data


df = load_data()
labels = df.classification.unique().tolist()


# SIDEBAR
st.sidebar.header("Parameters")
info_sidebar = st.sidebar.empty()

st.sidebar.subheader("Year")
year_to_filter = st.sidebar.slider('Choose the desired year', 2008, 2018, 2015)

st.sidebar.subheader("Table")
tabela = st.sidebar.empty()    

label_to_filter = st.sidebar.multiselect(
    label="Choose the classification of the occurrence",
    options=labels,
    default=["INCIDENT", 'ACCIDENT']
)

st.sidebar.markdown("""
The database of aeronautical events is managed by the ***Center for Investigation and Prevention of Accidents
Aeronautics (CENIPA)***.
""")

filtered_df = df[(df.date.dt.year == year_to_filter) & (df.classification.isin(label_to_filter))]

info_sidebar.info("{} selected occurrences.".format(filtered_df.shape[0]))

# MAIN
st.title("CENIPA - Aeronautical Accidents")
st.markdown(f"""
            ℹ️ Events classified as **{", ".join(label_to_filter)}**
            for the year **{year_to_filter}**.
            """)

if tabela.checkbox("Show data table"):
    st.write(filtered_df)

# MAP
st.subheader("Occurrence map")
st.map(filtered_df)

st.subheader("Locations with the highest number of occurrences")
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=-22.96592,
        longitude=-43.17896,
        zoom=3,
        pitch=50
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=filtered_df,
            disk_resolution=12,
            radius=30000,
            get_position='[longitude,latitude]',
            get_fill_color='[255, 255, 255, 255]',
            get_line_color="[255, 255, 255]",
            auto_highlight=True,
            elevation_scale=1500,
            # elevation_range=[0, 3000],
            # get_elevation="norm_price",
            pickable=True,
            extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_color='[255, 255, 255, 30]',
            get_radius=60000,
        ),
    ],
))

