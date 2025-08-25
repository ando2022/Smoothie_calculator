import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO

# ==== Configuration ====
DAILY_PROTEIN_NEED = 50  # g
DAILY_FIBER_NEED = 25    # g
TOTAL_SMOOTHIE_WEIGHT = 250  # g

# Layer proportions and colors
layers = [
    "Protein Source",
    "Grain / Carb Base",
    "Vegetable / Fruit",
    "Liquid / Extract",
    "Booster / Flavor Enhancer"
]
layer_proportions = [0.2, 0.2, 0.2, 0.3, 0.1]
layer_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

# ==== Load CSV ====
path = "smoothies_all_goals.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(path)
    df["IngredientList"] = df["Ingredients"].apply(lambda x: [i.strip() for i in x.split(",")])
    return df

df = load_data()

# ==== UI ====
st.set_page_config(layout="wide")
st.title("Smart Smoothie Generator")
st.markdown("Select your **goal** and **flavor**, and we’ll give you an optimized smoothie suggestion.")

# ==== Filter Selection ====
goal = st.selectbox("Wellness Goal", sorted(df["Goal"].unique()))
available_flavors = sorted(df[df["Goal"] == goal]["Flavor"].unique())
flavor = st.selectbox("Dominant Flavor", available_flavors)

# ==== Smoothie Display ====
if not df[(df["Goal"] == goal) & (df["Flavor"] == flavor)].empty:
    smoothie = df[(df["Goal"] == goal) & (df["Flavor"] == flavor)].sample(1).iloc[0]

    # Two-column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Smoothie for {goal} with {flavor} flavor")
        st.markdown(f"**Smoothie ID:** `{smoothie['SmoothieID']}`")
        st.markdown("**Ingredients:**")
        for ing in smoothie["IngredientList"]:
            st.markdown(f"- {ing}")

        st.markdown("---")
        st.markdown(f"**Protein:** `{smoothie['Total_Protein']}g`")
        st.markdown(f"**Fiber:** `{smoothie['Total_Fiber']}g`")

        st.markdown("### Remaining Nutrient Needs Today")
        remaining_protein = max(0, DAILY_PROTEIN_NEED - smoothie["Total_Protein"])
        remaining_fiber = max(0, DAILY_FIBER_NEED - smoothie["Total_Fiber"])
        st.write(f"• Protein still needed: `{remaining_protein}g`")
        st.write(f"• Fiber still needed: `{remaining_fiber}g`")

      
    with col2:
        # === Build Smoothie Visual ===
        ingredients = smoothie["IngredientList"]
        proportions = layer_proportions[:len(ingredients)]  # avoid mismatch

        fig, ax = plt.subplots(figsize=(2.5, 6), dpi=120)
        bottom = 0

        for i, (ingredient, prop) in enumerate(zip(ingredients, proportions)):
            height = prop
            color = layer_colors[i % len(layer_colors)]

            rect = patches.Rectangle((0.1, bottom), 0.8, height, facecolor=color, edgecolor='black')
            ax.add_patch(rect)

            weight = round(prop * TOTAL_SMOOTHIE_WEIGHT)
            label = f"{ingredient} {weight}g"
            ax.text(0.5, bottom + height / 2, label,
                    ha='center', va='center', fontsize=7,
                    color='white', weight='bold')
            bottom += height

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        st.image(buf, use_container_width=True)