import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 🌈 Palette de couleurs améliorée
COLOR_PALETTE = {
    'primary': '#636EFA',
    'secondary': '#EF553B',
    'accent': '#00CC96',
    'text': '#2C3E50',
    'background': '#F8F9FA',
    'dark': '#1E1E1E'
}

# 🎨 Configuration de la page
st.set_page_config(
    page_title="Tableau de Bord - Analyse des Ventes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🖌️ Style personnalisé
st.markdown(
    f"""
    <style>
    .main {{
        background-color: {COLOR_PALETTE['background']};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {COLOR_PALETTE['dark']};
    }}
    .stSelectbox, .stSlider, .stDateInput {{
        background-color: white;
    }}
    .css-1v3fvcr {{
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# 📊 Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("Données_propres.csv")
    df = df.drop(columns=['Unnamed: 0'], errors='ignore')
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['revenue'] = df['quantity'] * df['price']
    df['month_year'] = df['order_date'].dt.to_period('M').astype(str)
    return df

data = load_data()

# 🎛️ Sidebar avec filtres
with st.sidebar:
    st.title("🔧 Filtres")
    
    # Filtre par date
    min_date = data['order_date'].min().date()
    max_date = data['order_date'].max().date()
    date_range = st.date_input(
        "Période",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtre par ville
    cities = st.multiselect(
        "Villes",
        options=data['city'].unique(),
        default=data['city'].unique()
    )
    
    # Filtre par produit
    products = st.multiselect(
        "Produits",
        options=data['product'].unique(),
        default=data['product'].unique()
    )
    
    # Filtre par méthode de paiement
    payment_methods = st.multiselect(
        "Méthodes de paiement",
        options=data['payment_method'].unique(),
        default=data['payment_method'].unique()
    )

# Appliquer les filtres
filtered_data = data[
    (data['order_date'].dt.date >= date_range[0]) & 
    (data['order_date'].dt.date <= date_range[1]) &
    (data['city'].isin(cities)) &
    (data['product'].isin(products)) &
    (data['payment_method'].isin(payment_methods))
]

# 📌 Titre principal
st.title("📈 Tableau de Bord Interactif des Ventes")

# 🔢 Métriques clés
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total des ventes", f"{filtered_data['quantity'].sum():,} unités")
with col2:
    st.metric("Chiffre d'affaires", f"€{filtered_data['revenue'].sum():,.2f}")
with col3:
    st.metric("Commandes", filtered_data.shape[0])
with col4:
    st.metric("Clients uniques", filtered_data['customer_name'].nunique())

st.markdown("---")

# 📊 Section des visualisations
tab1, tab2 = st.tabs(["📈 Aperçu général", "🔍 Analyse détaillée"])

with tab1:
    # 📍 Graphique 1: Commandes par ville et produit
    st.header("Répartition des commandes")
    col1, col2 = st.columns(2)
    
    with col1:
        city_orders = filtered_data['city'].value_counts().reset_index()
        fig1 = px.bar(
            city_orders,
            x='city',
            y='count',
            title='Commandes par ville',
            color='city',
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        product_orders = filtered_data['product'].value_counts().reset_index()
        fig2 = px.pie(
            product_orders,
            names='product',
            values='count',
            title='Répartition par produit',
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # 📍 Graphique 2: Évolution temporelle
    st.header("Évolution temporelle")
    
    time_agg = st.radio(
        "Période d'agrégation",
        options=['Journalière', 'Mensuelle', 'Trimestrielle'],
        horizontal=True
    )
    
    freq_map = {'Journalière': 'D', 'Mensuelle': 'M', 'Trimestrielle': 'Q'}
    time_data = filtered_data.groupby(pd.Grouper(key='order_date', freq=freq_map[time_agg]))['revenue'].sum().reset_index()
    
    fig3 = px.line(
        time_data,
        x='order_date',
        y='revenue',
        title=f"Évolution du chiffre d'affaires ({time_agg.lower()})",
        markers=True,
        color_discrete_sequence=[COLOR_PALETTE['primary']]
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    # 📍 Graphique 3: Relation quantité-prix
    st.header("Analyse des produits")
    
    fig4 = px.scatter(
        filtered_data,
        x='quantity',
        y='price',
        color='product',
        size='revenue',
        hover_data=['customer_name', 'city', 'payment_method'],
        title='Relation entre quantité et prix par produit',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    # 📍 Graphique 4: Méthodes de paiement
    st.header("Analyse des paiements")
    col1, col2 = st.columns(2)
    
    with col1:
        payment_dist = filtered_data['payment_method'].value_counts().reset_index()
        fig5 = px.pie(
            payment_dist,
            names='payment_method',
            values='count',
            title='Méthodes de paiement',
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig5, use_container_width=True)
    
    with col2:
        payment_revenue = filtered_data.groupby('payment_method')['revenue'].sum().reset_index()
        fig6 = px.bar(
            payment_revenue,
            x='payment_method',
            y='revenue',
            title='Chiffre par méthode de paiement',
            color='payment_method',
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig6, use_container_width=True)
    
    # 📍 Graphique 5: Top clients
    st.header("Analyse des clients")
    top_clients = filtered_data.groupby('customer_name')['revenue'].sum().nlargest(10).reset_index()
    fig7 = px.bar(
        top_clients,
        x='customer_name',
        y='revenue',
        title='Top 10 clients par chiffre d\'affaires',
        color='customer_name',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    st.plotly_chart(fig7, use_container_width=True)

# � Pied de page
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <p>✨ Tableau de bord créé avec Streamlit et Plotly | © 2023</p>
    </div>
""", unsafe_allow_html=True)