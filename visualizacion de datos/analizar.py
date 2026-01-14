
"""
FAOSTAT Food Prices - Data Preparation for Visualization
Autor: Abdallah Tegguer
"""

import pandas as pd
import numpy as np
import os

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

OUTPUT_FOLDER = 'output'
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# =============================================================================
# PASO 1: CARGAR DATOS
# =============================================================================

print("=" * 60)
print("PASO 1: CARGANDO DATOS")
print("=" * 60)

# Dataset principal
df_main = pd.read_csv('Prices_E_All_Data.csv', encoding='latin-1')
print(f"Dataset principal cargado: {len(df_main):,} filas, {len(df_main.columns)} columnas")

# Datasets auxiliares
df_area_codes = pd.read_csv('Prices_E_AreaCodes.csv', encoding='latin-1')
df_item_codes = pd.read_csv('Prices_E_ItemCodes.csv', encoding='latin-1')
df_elements = pd.read_csv('Prices_E_Elements.csv', encoding='latin-1')
df_flags = pd.read_csv('Prices_E_Flags.csv', encoding='latin-1')

print(f"AreaCodes cargado: {len(df_area_codes)} registros")
print(f"ItemCodes cargado: {len(df_item_codes)} registros")
print(f"Elements cargado: {len(df_elements)} registros")
print(f"Flags cargado: {len(df_flags)} registros")

# =============================================================================
# PASO 2: VALIDACIÓN ESTRUCTURAL
# =============================================================================

print("\n" + "=" * 60)
print("PASO 2: VALIDACIÓN ESTRUCTURAL")
print("=" * 60)

# Limpiar nombres de columnas en auxiliares (quitar espacios)
df_area_codes.columns = df_area_codes.columns.str.strip()
df_item_codes.columns = df_item_codes.columns.str.strip()
df_elements.columns = df_elements.columns.str.strip()
df_flags.columns = df_flags.columns.str.strip()

# Validación con AreaCodes
area_codes_in_main = set(df_main['Area Code'].unique())
area_codes_in_aux = set(df_area_codes['Area Code'].unique())
area_match = area_codes_in_main.issubset(area_codes_in_aux)
print(f"Validación Area Codes: {'OK' if area_match else 'MISMATCH'}")
print(f"  - Códigos en main: {len(area_codes_in_main)}")
print(f"  - Códigos en auxiliar: {len(area_codes_in_aux)}")

# Validación con ItemCodes
item_codes_in_main = set(df_main['Item Code'].unique())
item_codes_in_aux = set(df_item_codes['Item Code'].unique())
item_match = item_codes_in_main.issubset(item_codes_in_aux)
print(f"Validación Item Codes: {'OK' if item_match else 'MISMATCH'}")
print(f"  - Códigos en main: {len(item_codes_in_main)}")
print(f"  - Códigos en auxiliar: {len(item_codes_in_aux)}")

# Validación con Elements
element_codes_in_main = set(df_main['Element Code'].unique())
element_codes_in_aux = set(df_elements['Element Code'].unique())
element_match = element_codes_in_main.issubset(element_codes_in_aux)
print(f"Validación Element Codes: {'OK' if element_match else 'MISMATCH'}")
print(f"  - Códigos en main: {len(element_codes_in_main)}")
print(f"  - Códigos en auxiliar: {len(element_codes_in_aux)}")

# Merge de validación con AreaCodes para obtener M49 Code
df_area_codes_clean = df_area_codes[['Area Code', 'M49 Code']].copy()
df_area_codes_clean.columns = ['Area Code', 'M49_Code_Validated']
df_validated = df_main.merge(df_area_codes_clean, on='Area Code', how='left')

validation_success = df_validated['M49_Code_Validated'].notna().sum()
print(f"Merge de validación con AreaCodes: {validation_success:,} / {len(df_validated):,} registros validados")

# No conservamos la columna extra, solo era para validación
del df_validated

# Mostrar elementos disponibles
print("\nElementos disponibles en el dataset:")
for _, row in df_elements.iterrows():
    code = row['Element Code']
    name = row['Element']
    count = len(df_main[df_main['Element Code'] == code])
    print(f"  - {code}: {name} ({count:,} registros)")

# Mostrar flags disponibles
print("\nFlags de calidad disponibles:")
for _, row in df_flags.iterrows():
    print(f"  - {row['Flag']}: {row['Description']}")

# =============================================================================
# PASO 3: FILTRADO
# =============================================================================

print("\n" + "=" * 60)
print("PASO 3: FILTRADO POR ELEMENTO COMPARABLE")
print("=" * 60)

# Filtrar solo Producer Price Index (5539) para comparabilidad internacional
ELEMENT_CODE_PPI = 5539
df_filtered = df_main[df_main['Element Code'] == ELEMENT_CODE_PPI].copy()

print(f"Filtrado por Element Code {ELEMENT_CODE_PPI} (Producer Price Index)")
print(f"  - Registros antes: {len(df_main):,}")
print(f"  - Registros después: {len(df_filtered):,}")
print(f"  - Países únicos: {df_filtered['Area'].nunique()}")
print(f"  - Productos únicos: {df_filtered['Item'].nunique()}")

# =============================================================================
# PASO 4: RESHAPE A FORMATO LONG
# =============================================================================

print("\n" + "=" * 60)
print("PASO 4: TRANSFORMACIÓN A FORMATO LONG")
print("=" * 60)

# Identificar columnas de años (valores) y columnas de flags
year_value_cols = [col for col in df_filtered.columns if col.startswith('Y') and col[1:].isdigit() and not col.endswith('F')]
year_flag_cols = [col for col in df_filtered.columns if col.startswith('Y') and col.endswith('F')]

print(f"Columnas de valores identificadas: {len(year_value_cols)} (Y1991 a Y2024)")
print(f"Columnas de flags identificadas: {len(year_flag_cols)} (no se usan en cálculos)")

# Seleccionar solo columnas necesarias para el reshape
id_columns = ['Area Code', 'Area', 'Item Code', 'Item', 'Element Code', 'Element']
df_for_melt = df_filtered[id_columns + year_value_cols].copy()

# Pivotear a formato long
df_long = df_for_melt.melt(
    id_vars=id_columns,
    value_vars=year_value_cols,
    var_name='Year',
    value_name='Price'
)

# Limpiar columna Year
df_long['Year'] = df_long['Year'].str.replace('Y', '').astype(int)

# Simplificar estructura final
df_long = df_long[['Area', 'Item', 'Element', 'Year', 'Price']].copy()

print(f"Transformación completada:")
print(f"  - Registros en formato long: {len(df_long):,}")
print(f"  - Estructura: {list(df_long.columns)}")

# =============================================================================
# PASO 5: LIMPIEZA DE DATOS
# =============================================================================

print("\n" + "=" * 60)
print("PASO 5: LIMPIEZA DE DATOS")
print("=" * 60)

# Contar valores faltantes antes
missing_before = df_long['Price'].isna().sum()
total_before = len(df_long)

print(f"Valores faltantes antes de limpieza: {missing_before:,} / {total_before:,} ({missing_before/total_before*100:.1f}%)")

# Eliminar filas con Price nulo (NO interpolamos)
df_clean = df_long.dropna(subset=['Price']).copy()

# Verificar después
missing_after = df_clean['Price'].isna().sum()
total_after = len(df_clean)

print(f"Registros después de eliminar nulos: {total_after:,}")
print(f"Registros eliminados: {total_before - total_after:,}")

# Verificar rango de años con datos
year_coverage = df_clean.groupby('Year').size()
print(f"Cobertura temporal: {df_clean['Year'].min()} - {df_clean['Year'].max()}")
print(f"Años con datos: {len(year_coverage)}")

# =============================================================================
# PASO 6: CÁLCULO DE MÉTRICAS
# =============================================================================

print("\n" + "=" * 60)
print("PASO 6: CÁLCULO DE MÉTRICAS")
print("=" * 60)

# --- 6.1: Asignación de regiones geográficas ---
print("\n6.1 Asignando regiones geográficas...")

REGION_MAPPING = {
    'Africa': [
        'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi',
        'Cabo Verde', 'Cameroon', 'Central African Republic', 'Chad', 'Comoros',
        'Congo', "Côte d'Ivoire", 'Democratic Republic of the Congo', 'Egypt',
        'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 'Gambia',
        'Ghana', 'Guinea', 'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia',
        'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius',
        'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda',
        'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone',
        'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Togo', 'Tunisia',
        'Uganda', 'United Republic of Tanzania', 'Zambia', 'Zimbabwe'
    ],
    'Americas': [
        'Antigua and Barbuda', 'Argentina', 'Bahamas', 'Barbados', 'Belize',
        'Bolivia (Plurinational State of)', 'Brazil', 'Canada', 'Chile',
        'Colombia', 'Costa Rica', 'Cuba', 'Dominica', 'Dominican Republic',
        'Ecuador', 'El Salvador', 'Grenada', 'Guatemala', 'Guyana', 'Haiti',
        'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Paraguay',
        'Peru', 'Puerto Rico', 'Saint Kitts and Nevis', 'Saint Lucia',
        'Saint Vincent and the Grenadines', 'Suriname', 'Trinidad and Tobago',
        'United States of America', 'Uruguay', 'Venezuela (Bolivarian Republic of)'
    ],
    'Asia': [
        'Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan',
        'Brunei Darussalam', 'Cambodia', 'China, mainland', 'Cyprus', 'Georgia',
        'India', 'Indonesia', 'Iran (Islamic Republic of)', 'Iraq', 'Israel',
        'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan',
        "Lao People's Democratic Republic", 'Lebanon', 'Malaysia', 'Maldives',
        'Mongolia', 'Myanmar', 'Nepal', 'Oman', 'Pakistan', 'Palestine',
        'Philippines', 'Qatar', 'Republic of Korea', 'Saudi Arabia', 'Singapore',
        'Sri Lanka', 'Syrian Arab Republic', 'Tajikistan', 'Thailand',
        'Timor-Leste', 'Türkiye', 'Turkmenistan', 'United Arab Emirates',
        'Uzbekistan', 'Viet Nam', 'Yemen', "Democratic People's Republic of Korea"
    ],
    'Europe': [
        'Albania', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina',
        'Bulgaria', 'Croatia', 'Czechia', 'Denmark', 'Estonia', 'Finland',
        'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy',
        'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Netherlands (Kingdom of the)',
        'North Macedonia', 'Norway', 'Poland', 'Portugal', 'Republic of Moldova',
        'Romania', 'Russian Federation', 'Serbia', 'Slovakia', 'Slovenia',
        'Spain', 'Sweden', 'Switzerland', 'Ukraine',
        'United Kingdom of Great Britain and Northern Ireland'
    ],
    'Oceania': [
        'Australia', 'Cook Islands', 'Fiji', 'French Polynesia', 'New Caledonia',
        'New Zealand', 'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga',
        'Vanuatu'
    ]
}

def assign_region(area):
    for region, countries in REGION_MAPPING.items():
        if area in countries:
            return region
    return 'Other'

df_clean['Region'] = df_clean['Area'].apply(assign_region)

region_distribution = df_clean.groupby('Region')['Area'].nunique()
print("Distribución por región:")
for region, count in region_distribution.items():
    print(f"  - {region}: {count} países")

# --- 6.2: Categorización de productos ---
print("\n6.2 Categorizando productos...")

PRODUCT_CATEGORIES = {
    'Cereals': [
        'Wheat', 'Rice', 'Maize (corn)', 'Barley', 'Sorghum', 'Millet',
        'Oats', 'Rye', 'Triticale', 'Buckwheat', 'Quinoa', 'Fonio',
        'Cereals, primary', 'Coarse Grain, Total', 'Cereals (Rice Milled Eqv)',
        'Canary seed', 'Mixed grain', 'Cereals n.e.c.'
    ],
    'Fruits': [
        'Apples', 'Oranges', 'Bananas', 'Grapes', 'Mangoes, guavas and mangosteens',
        'Pineapples', 'Papayas', 'Lemons and limes', 'Tangerines, mandarins, clementines',
        'Peaches and nectarines', 'Plums and sloes', 'Strawberries', 'Watermelons',
        'Cantaloupes and other melons', 'Pomelos and grapefruits', 'Pears', 'Apricots',
        'Cherries', 'Sour cherries', 'Figs', 'Dates', 'Kiwi fruit', 'Avocados',
        'Persimmons', 'Cashewapple', 'Fruit Primary', 'Fruit excl Melons, Total',
        'Citrus Fruit, Total', 'Fruit Incl Melons', 'Other citrus fruit, n.e.c.',
        'Other tropical fruits, n.e.c.', 'Blueberries', 'Raspberries', 'Currants',
        'Gooseberries', 'Cranberries', 'Other pome fruits', 'Other stone fruits',
        'Other berries and fruits of the genus vaccinium n.e.c.', 'Other fruits, n.e.c.',
        'Locust beans (carobs)', 'Plantains and cooking bananas', 'Plantains',
        'Cooking bananas', 'Bananas', 'Other bananas (excluding cavendish and cooking bananas)',
        'Bananas cavendish', 'Quinces'
    ],
    'Vegetables': [
        'Tomatoes', 'Potatoes', 'Onions and shallots, dry (excluding dehydrated)',
        'Onions and shallots, green', 'Carrots and turnips', 'Cabbages',
        'Lettuce and chicory', 'Cucumbers and gherkins', 'Eggplants (aubergines)',
        'Chillies and peppers, green (Capsicum spp. and Pimenta spp.)', 'Spinach',
        'Cauliflowers and broccoli', 'Asparagus', 'Green garlic', 'Peas, green',
        'Beans, green', 'String beans', 'Other beans, green',
        'Broad beans and horse beans, green', 'Pumpkins, squash and gourds', 'Okra',
        'Green corn (maize)', 'Mushrooms and truffles', 'Artichokes',
        'Vegetables Primary', 'Vegetables&Melons, Total', 'Vegetables',
        'Leeks and other alliaceous vegetables', 'Other vegetables, fresh n.e.c.',
        'Chicory roots'
    ],
    'Meat': [
        'Meat of cattle with the bone, fresh or chilled',
        'Meat of cattle with the bone, fresh or chilled (biological)',
        'Meat of chickens, fresh or chilled',
        'Meat of chickens, fresh or chilled (biological)',
        'Meat of sheep, fresh or chilled',
        'Meat of sheep, fresh or chilled (biological)',
        'Meat of goat, fresh or chilled',
        'Meat of goat, fresh or chilled (biological)',
        'Meat of pig with the bone, fresh or chilled',
        'Meat of pig with the bone, fresh or chilled (biological)',
        'Meat of turkeys, fresh or chilled',
        'Meat of turkeys, fresh or chilled (biological)',
        'Meat of ducks, fresh or chilled',
        'Meat of ducks, fresh or chilled (biological)',
        'Meat of geese, fresh or chilled',
        'Meat of geese, fresh or chilled (biological)',
        'Meat of rabbits and hares, fresh or chilled',
        'Meat of rabbits and hares, fresh or chilled (biological)',
        'Meat, Total', 'Meat Liveweight, Total',
        'Horse meat, fresh or chilled',
        'Horse meat, fresh or chilled (biological)',
        'Meat of asses, fresh or chilled',
        'Meat of asses, fresh or chilled (biological)',
        'Meat of mules, fresh or chilled',
        'Meat of mules, fresh or chilled (biological)',
        'Meat of camels, fresh or chilled',
        'Meat of camels, fresh or chilled (biological)',
        'Meat of other domestic camelids, fresh or chilled',
        'Meat of other domestic camelids, fresh or chilled (biological)',
        'Meat of other domestic rodents, fresh or chilled',
        'Meat of other domestic rodents, fresh or chilled (biological)',
        'Other meat of mammals, fresh or chilled',
        'Game meat, fresh, chilled or frozen',
        'Meat of pigeons and other birds n.e.c., fresh, chilled or frozen',
        'Meat of pigeons and other birds n.e.c., fresh, chilled or frozen (biological)',
        'Meat of buffalo, fresh or chilled',
        'Meat of buffalo, fresh or chilled (biological)'
    ],
    'Dairy & Eggs': [
        'Raw milk of cattle', 'Raw milk of buffalo', 'Raw milk of sheep',
        'Raw milk of goats', 'Raw milk of camel', 'Milk, Total',
        'Hen eggs in shell, fresh', 'Eggs Primary',
        'Eggs from other birds in shell, fresh, n.e.c.'
    ],
    'Oilseeds': [
        'Soya beans', 'Groundnuts, excluding shelled', 'Sunflower seed',
        'Rape or colza seed', 'Cotton seed', 'Oil palm fruit', 'Palm kernels',
        'Coconuts, in shell', 'Sesame seed', 'Linseed', 'Castor oil seeds',
        'Safflower seed', 'Mustard seed', 'Poppy seed', 'Olives',
        'Oilcrops, Oil Equivalent', 'Karite nuts (sheanuts)', 'Melonseed',
        'Jojoba seeds', 'Tallowtree seeds', 'Hempseed', 'Other oil seeds, n.e.c.'
    ],
    'Roots & Tubers': [
        'Cassava, fresh', 'Sweet potatoes', 'Yams', 'Taro', 'Yautia',
        'Roots and Tubers, Total',
        'Edible roots and tubers with high starch or inulin content, n.e.c., fresh'
    ],
    'Pulses': [
        'Beans, dry', 'Peas, dry', 'Lentils, dry', 'Chick peas, dry',
        'Broad beans and horse beans, dry', 'Cow peas, dry', 'Pigeon peas, dry',
        'Bambara beans, dry', 'Vetches', 'Lupins', 'Pulses, Total',
        'Other pulses n.e.c.'
    ],
    'Beverages': [
        'Coffee, green', 'Cocoa beans', 'Tea leaves', 'Maté leaves',
        'Tea nes (herbal tea)', 'Hop cones'
    ],
    'Sugar Crops': [
        'Sugar cane', 'Sugar beet', 'Other sugar crops n.e.c.'
    ],
    'Nuts': [
        'Almonds, in shell', 'Walnuts, in shell', 'Hazelnuts, in shell',
        'Pistachios, in shell', 'Cashew nuts, in shell', 'Brazil nuts, in shell',
        'Chestnuts, in shell', 'Areca nuts', 'Kola nuts', 'Treenuts, Total',
        'Other nuts (excluding wild edible nuts and groundnuts), in shell, n.e.c.'
    ],
    'Spices': [
        'Pepper (Piper spp.), raw',
        'Chillies and peppers, dry (Capsicum spp., Pimenta spp.), raw',
        'Vanilla, raw', 'Cinnamon and cinnamon-tree flowers, raw',
        'Cloves (whole stems), raw', 'Nutmeg, mace, cardamoms, raw',
        'Anise, badian, coriander, cumin, caraway, fennel and juniper berries, raw',
        'Ginger, raw', 'Other stimulant, spice and aromatic crops, n.e.c.',
        'Peppermint, spearmint'
    ],
    'Fibers': [
        'Seed cotton, unginned', 'Cotton lint, ginned',
        'Jute, raw or retted', 'Kenaf, and other textile bast fibres, raw or retted',
        'Flax, processed but not spun', 'True hemp, raw or retted',
        'Ramie, raw or retted', 'Sisal, raw', 'Agave fibres, raw, n.e.c.',
        'Abaca, manila hemp, raw', 'Fibre Crops Primary',
        'Other fibre crops, raw, n.e.c.', 'Jute & Jute-like Fibres'
    ],
    'Other Industrial': [
        'Unmanufactured tobacco', 'Natural rubber in primary forms',
        'Balata, gutta-percha, guayule, chicle and similar natural gums in primary forms or in plates, sheets or strip',
        'Pyrethrum, dried flowers', 'Natural honey', 'Beeswax',
        'Silk-worm cocoons suitable for reeling',
        'Shorn wool, greasy, including fleece-washed shorn wool',
        'Snails, fresh, chilled, frozen, dried, salted or in brine, except sea snails',
        'Vegetable tallow', 'Stillingia oil', 'Kapok fruit', 'Palm oil',
        'Tung nuts'
    ],
    'Aggregates': [
        'Agriculture', 'Livestock', 'Crops, primary'
    ]
}

def assign_category(item):
    for category, items in PRODUCT_CATEGORIES.items():
        if item in items:
            return category
    return 'Other'

df_clean['Product_Category'] = df_clean['Item'].apply(assign_category)

category_distribution = df_clean['Product_Category'].value_counts()
print("Distribución por categoría de producto:")
for category, count in category_distribution.head(15).items():
    print(f"  - {category}: {count:,} registros")

# --- 6.3: Variación interanual (Year-over-Year) ---
print("\n6.3 Calculando variación interanual...")

df_clean = df_clean.sort_values(['Area', 'Item', 'Year'])

df_clean['Price_Lag'] = df_clean.groupby(['Area', 'Item'])['Price'].shift(1)
df_clean['YoY_Change'] = ((df_clean['Price'] - df_clean['Price_Lag']) / df_clean['Price_Lag']) * 100
df_clean['YoY_Change'] = df_clean['YoY_Change'].replace([np.inf, -np.inf], np.nan)

df_clean = df_clean.drop(columns=['Price_Lag'])

yoy_valid = df_clean['YoY_Change'].notna().sum()
print(f"Variaciones YoY calculadas: {yoy_valid:,} registros con valor válido")

# --- 6.4: Métricas a nivel de país ---
print("\n6.4 Calculando métricas a nivel de país...")

def calculate_country_metrics(group):
    prices = group.sort_values('Year')['Price'].values
    years = group.sort_values('Year')['Year'].values
    
    # Volatilidad
    if len(prices) >= 5:
        pct_changes = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                pct_changes.append(((prices[i] - prices[i-1]) / prices[i-1]) * 100)
        volatility = np.std(pct_changes) if len(pct_changes) >= 3 else np.nan
    else:
        volatility = np.nan
    
    # Tendencia 2010-2023
    price_2010 = group[group['Year'] == 2010]['Price'].values
    price_2023 = group[group['Year'] == 2023]['Price'].values
    if len(price_2010) > 0 and len(price_2023) > 0 and price_2010[0] > 0:
        trend = ((price_2023[0] - price_2010[0]) / price_2010[0]) * 100
    else:
        trend = np.nan
    
    return pd.Series({
        'Avg_Price': np.mean(prices),
        'Min_Price': np.min(prices),
        'Max_Price': np.max(prices),
        'Volatility': volatility,
        'Trend_2010_2023': trend,
        'Data_Points': len(prices),
        'Year_Min': int(np.min(years)),
        'Year_Max': int(np.max(years))
    })

country_metrics = df_clean.groupby(['Area', 'Region']).apply(
    calculate_country_metrics, include_groups=False
).reset_index()

# Redondear valores
for col in ['Avg_Price', 'Min_Price', 'Max_Price', 'Volatility', 'Trend_2010_2023']:
    country_metrics[col] = country_metrics[col].round(2)

print(f"Métricas calculadas para {len(country_metrics)} países")

# --- 6.5: Métricas a nivel de producto ---
print("\n6.5 Calculando métricas a nivel de producto...")

product_metrics = df_clean.groupby(['Item', 'Product_Category']).apply(
    calculate_country_metrics, include_groups=False
).reset_index()

for col in ['Avg_Price', 'Min_Price', 'Max_Price', 'Volatility', 'Trend_2010_2023']:
    product_metrics[col] = product_metrics[col].round(2)

print(f"Métricas calculadas para {len(product_metrics)} productos")

# --- 6.6: Agregados regionales ---
print("\n6.6 Calculando agregados regionales...")

regional_aggregates = df_clean.groupby(['Region', 'Year', 'Product_Category']).agg({
    'Price': ['mean', 'std', 'min', 'max', 'count']
}).reset_index()

regional_aggregates.columns = [
    'Region', 'Year', 'Product_Category',
    'Avg_Price', 'Std_Price', 'Min_Price', 'Max_Price', 'Count'
]

for col in ['Avg_Price', 'Std_Price', 'Min_Price', 'Max_Price']:
    regional_aggregates[col] = regional_aggregates[col].round(2)

print(f"Agregados regionales: {len(regional_aggregates):,} registros")

# --- 6.7: Métricas por país y categoría de producto ---
print("\n6.7 Calculando métricas por país y categoría...")

country_category_metrics = df_clean.groupby(['Area', 'Region', 'Product_Category']).apply(
    calculate_country_metrics, include_groups=False
).reset_index()

for col in ['Avg_Price', 'Min_Price', 'Max_Price', 'Volatility', 'Trend_2010_2023']:
    country_category_metrics[col] = country_category_metrics[col].round(2)

print(f"Métricas país-categoría: {len(country_category_metrics):,} combinaciones")

# =============================================================================
# PASO 7: EXPORTAR ARCHIVOS CSV
# =============================================================================

print("\n" + "=" * 60)
print("PASO 7: EXPORTANDO ARCHIVOS CSV")
print("=" * 60)

# 1. Dataset limpio en formato long
output_1 = os.path.join(OUTPUT_FOLDER, '01_FAOSTAT_Prices_Clean_Long.csv')
df_clean.to_csv(output_1, index=False)
print(f"✓ {output_1}")
print(f"  Registros: {len(df_clean):,}")

# 2. Métricas a nivel de país
output_2 = os.path.join(OUTPUT_FOLDER, '02_Country_Metrics.csv')
country_metrics.to_csv(output_2, index=False)
print(f"✓ {output_2}")
print(f"  Registros: {len(country_metrics):,}")

# 3. Métricas a nivel de producto
output_3 = os.path.join(OUTPUT_FOLDER, '03_Product_Metrics.csv')
product_metrics.to_csv(output_3, index=False)
print(f"✓ {output_3}")
print(f"  Registros: {len(product_metrics):,}")

# 4. Agregados regionales
output_4 = os.path.join(OUTPUT_FOLDER, '04_Regional_Aggregates.csv')
regional_aggregates.to_csv(output_4, index=False)
print(f"✓ {output_4}")
print(f"  Registros: {len(regional_aggregates):,}")

# 5. Métricas país-categoría
output_5 = os.path.join(OUTPUT_FOLDER, '05_Country_Category_Metrics.csv')
country_category_metrics.to_csv(output_5, index=False)
print(f"✓ {output_5}")
print(f"  Registros: {len(country_category_metrics):,}")

# =============================================================================
# RESUMEN FINAL
# =============================================================================

print("\n" + "=" * 60)
print("PROCESO COMPLETADO")
print("=" * 60)
print(f"""
Archivos generados en '{OUTPUT_FOLDER}/':

1. 01_FAOSTAT_Prices_Clean_Long.csv
   - Dataset principal en formato tidy
   - Columnas: Area, Item, Element, Year, Price, Region, Product_Category, YoY_Change
   - Uso: Base para todas las visualizaciones

2. 02_Country_Metrics.csv
   - Métricas agregadas por país
   - Columnas: Area, Region, Avg_Price, Volatility, Trend_2010_2023, etc.
   - Uso: Mapa coroplético, ranking de países

3. 03_Product_Metrics.csv
   - Métricas agregadas por producto
   - Columnas: Item, Product_Category, Avg_Price, Volatility, Trend_2010_2023, etc.
   - Uso: Scatter plot volatilidad vs tendencia

4. 04_Regional_Aggregates.csv
   - Promedios por región, año y categoría de producto
   - Uso: Area charts, comparaciones regionales

5. 05_Country_Category_Metrics.csv
   - Métricas detalladas por país y categoría de producto
   - Uso: Análisis granular, drill-down

""")