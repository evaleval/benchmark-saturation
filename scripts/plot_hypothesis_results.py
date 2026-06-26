import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load Data
try:
    df = pd.read_csv('manual_annotation_data.csv')
except FileNotFoundError:
    df = pd.read_csv('manual_annotation_data.csv')

# Clean junk rows
df = df.dropna(subset=['Name']).drop_duplicates(subset=['Name'])

# 2. Preprocessing & Hypothesis Definitions
df['Released Date'] = pd.to_datetime(df['Released Date'], errors='coerce')
ref_date = pd.to_datetime('2025-11-01')
df['Age_Months'] = (ref_date - df['Released Date']) / pd.Timedelta(days=30.44)
df['Is_Saturated'] = df['Saturation Index (interpreted)'].apply(lambda x: 1 if x in ['High', 'Very high'] else 0)
df['Saturation_Index'] = df['Saturation Index']
df['Status'] = df['Saturation Index (interpreted)'].apply(lambda x: 'Saturated' if x in ['High', 'Very high'] else 'Not Saturated')

# Define Categorization Columns
df['Access_Type'] = df['Publically v/s Privately available'].fillna('Unknown')
df['Language_Category'] = df['Languages included'].apply(lambda x: 'English-Only' if str(x).strip() == 'English' else 'Multilingual')

def cat_curation(x):
    s = str(x).lower()
    is_auto = any(k in s for k in ['llm', 'program', 'synthetic', 'auto', 'generated'])
    is_human = any(k in s for k in ['human', 'expert', 'crowd'])
    if is_auto and is_human: return 'Human + Auto'
    if is_auto and not is_human: return 'Fully Synthetic'
    if 'expert' in s: return 'Expert Human'
    if 'crowd' in s: return 'Crowdsourced Human'
    return 'Other'
df['Curation_Class'] = df['Dataset curation tags'].apply(cat_curation)

def cat_issues(x):
    s = str(x).lower()
    return 'No Known Issues' if (pd.isna(x) or any(k in s for k in ['no known issues', 'clean', 'none'])) else 'Documented Issues'
df['Issue_Status'] = df['Dataset-related issues'].apply(cat_issues)

def cat_format(x):
    s = str(x).lower()
    if 'mcq' in s or 'multiple choice' in s: return 'Closed-Ended'
    return 'Open-Ended' if any(k in s for k in ['free-form', 'open', 'code', 'generation']) else 'Other'
df['Format_Class'] = df['Task Output Format'].apply(cat_format)

def cat_template(row):
    tags = str(row.get('Dataset curation tags', '')).lower()
    notes = str(row.get('Literal diversity Notes', '')).lower()
    if 'template' in tags or 'template' in notes or 'programatically' in tags or 'synthetic' in tags:
        return 'Templated'
    return 'Non-Templated'
df['Template_Class'] = df.apply(cat_template, axis=1)

# Helper function
def prepare_labels_n(data, col, order):
    subset = data[data[col].isin(order)].copy()
    counts = subset[col].value_counts()
    label_map = {cat: f"{cat}\n(N={counts.get(cat, 0)})" for cat in order}
    subset['Label'] = subset[col].map(label_map)
    order_n = [label_map[cat] for cat in order]
    return subset, order_n

# 3. Setup Grid: target layout
sns.set_style("whitegrid")

fig, axes = plt.subplots(3, 4, figsize=(20, 14))
plt.subplots_adjust(hspace=0.45, wspace=0.35)

# Add group headers
fig.text(
    0.25, 0.98,
    "Group A: Age-Balanced Distributions\n(Box Plots show index distribution)",
    ha="center", va="top", fontsize=20, fontweight="bold"
)

fig.text(
    0.75, 0.98,
    "Group B: Temporal Dynamics\n(Scatter Plots show Age vs Saturation)",
    ha="center", va="top", fontsize=20, fontweight="bold"
)

configs = {
    'H1': ('Access_Type', 'Test Set Access', ['Public', 'Private'], 'box'),
    'H2': ('Language_Category', 'Language Coverage', ['English-Only', 'Multilingual'], 'scatter'),
    'H3': ('Curation_Class', 'Synthetic vs. Human', ['Expert Human', 'Human + Auto', 'Crowdsourced Human', 'Fully Synthetic'], 'scatter'),
    'H4': ('Issue_Status', 'Data Quality', ['No Known Issues', 'Documented Issues'], 'scatter'),
    'H5': ('Format_Class', 'Output Format', ['Closed-Ended', 'Open-Ended'], 'box'),
    'H6': ('Template_Class', 'Template Diversity', ['Non-Templated', 'Templated'], 'box')
}

# Desired subplot positions:
# Left group: H1, H5, H6 each with bar + box
# Right group: H2, H3, H4 each with bar + scatter
layout = [
    ('H1', 0, 0), ('H1_box', 0, 1), ('H2', 0, 2), ('H2_scatter', 0, 3),
    ('H5', 1, 0), ('H5_box', 1, 1), ('H3', 1, 2), ('H3_scatter', 1, 3),
    ('H6', 2, 0), ('H6_box', 2, 1), ('H4', 2, 2), ('H4_scatter', 2, 3),
]

set2_palette = sns.color_palette("Set2")

for plot_id, row, col_pos in layout:
    hid = plot_id.split('_')[0]
    col, title, order, p_type = configs[hid]

    sub_df, order_n = prepare_labels_n(df, col, order)
    current_palette = set2_palette[:len(order)]
    ax = axes[row, col_pos]

    # Bar plots
    if '_' not in plot_id:
        rates = sub_df.groupby('Label', observed=True)['Is_Saturated'].mean().reindex(order_n).reset_index()

        sns.barplot(
            data=rates,
            x='Label',
            y='Is_Saturated',
            ax=ax,
            order=order_n,
            palette=current_palette,
            edgecolor=".2",
            alpha=1.0
        )

        ax.set_title(f"{hid}: {title}", fontweight='bold', fontsize=14)
        ax.set_xlabel("")
        ax.set_ylabel("Saturation Rate")
        ax.set_ylim(0, 0.75)
        ax.tick_params(axis='x', rotation=20 if hid == 'H3' else 0)

    # Box plots
    elif 'box' in plot_id:
        sns.boxplot(
            data=sub_df,
            x='Label',
            y='Saturation_Index',
            ax=ax,
            order=order_n,
            palette=current_palette,
            boxprops=dict(alpha=1.0),
            fliersize=0
        )

        sns.stripplot(
            data=sub_df,
            x='Label',
            y='Saturation_Index',
            ax=ax,
            order=order_n,
            color=".15",
            alpha=0.7,
            size=5,
            jitter=True
        )

        ax.set_title(f"{hid} Saturation Distribution", fontweight='bold', fontsize=14)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_ylim(-0.05, 1.05)
        ax.tick_params(axis='x', rotation=0)

    # Scatter plots
    elif 'scatter' in plot_id:
        color_dict = dict(zip(order, current_palette))

        sns.scatterplot(
            data=sub_df,
            x='Age_Months',
            y='Saturation_Index',
            hue=col,
            hue_order=order,
            style='Status',
            markers={"Saturated": "X", "Not Saturated": "o"},
            s=100,
            alpha=0.9,
            ax=ax,
            palette=color_dict
        )

        ax.set_title(f"{hid} Saturation vs. Benchmark Age", fontweight='bold', fontsize=14)
        ax.set_xlabel("Age (Months)")
        ax.set_ylabel("")
        ax.set_ylim(-0.05, 1.05)

        if ax.get_legend():
            ax.get_legend().remove()

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig('H1-H6-rearranged.pdf')
plt.show()
