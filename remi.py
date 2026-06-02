import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Utilisez un "r" avant les guillemets pour éviter les problèmes de slashs Windows
df = pd.read_csv(r'c:\Users\remde\Documents\test\WorldCupShootouts.csv')

print(df.head())


# ============================================================
# Penalty Shootouts Analysis
# ============================================================
def get_area(zone):
    if zone in (1, 4, 7):
        return 1  # Left
    elif zone in (2, 5, 8):
        return 2  # Middle
    elif zone in (3, 6, 9):
        return 3  # Right
    else:
        return 0  # Hors cadre / zone inconnue


df['Area'] = df['Zone'].apply(get_area)
print(df.head())

df_droitier = df[df['Foot'] == 'R'].copy()
df_gaucher = df[df['Foot'] == 'L'].copy()

# Copie où les tirs hors cadre sont marqués Area = 0
df_hors_cadre = df.copy()
df_hors_cadre.loc[df_hors_cadre['OnTarget'] == 0, 'Area'] = 0


# ============================================================
# Zone préférée selon le pied (tirs cadrés uniquement)
# ============================================================
# On se restreint aux tirs cadrés pour comparer des zones réelles (1/2/3),
# en excluant les Area = 0 (hors cadre / inconnu).
df_pref = df_hors_cadre[df_hors_cadre['Area'] != 0]

df_pct = (
    df_pref.groupby('Foot')['Area']
    .value_counts(normalize=True)
    .mul(100)
    .rename('Percentage')
    .reset_index()
)

sns.barplot(x='Foot', y='Percentage', hue='Area', data=df_pct)
plt.xlabel('Pied')
plt.ylabel('Pourcentage (%)')
plt.title('Zone préférée selon le pied')
plt.legend(title='Zone')
plt.show()


# ============================================================
# Répartition des buts par zone (droitiers vs gauchers)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

labels = ['Left', 'Middle', 'Right']

# Droitiers -> subplot de gauche
goals_droitier = (
    df_droitier[df_droitier['Goal'] == 1]
    .groupby('Area')
    .size()
    .reindex([1, 2, 3], fill_value=0)  # garantit exactement 3 parts dans l'ordre
)
axes[0].pie(goals_droitier, labels=labels, autopct='%1.1f%%')
axes[0].set_title('Droitiers', fontweight='bold')

# Gauchers -> subplot de droite
goals_gaucher = (
    df_gaucher[df_gaucher['Goal'] == 1]
    .groupby('Area')
    .size()
    .reindex([1, 2, 3], fill_value=0)
)
axes[1].pie(goals_gaucher, labels=labels, autopct='%1.1f%%')
axes[1].set_title('Gauchers', fontweight='bold')

plt.show()


# ============================================================
# Pourcentage d'arrêts du gardien selon la zone (tirs cadrés)
# ============================================================
df_cadres = df_hors_cadre[df_hors_cadre['OnTarget'] == 1]

# Nombre total de tirs cadrés par zone
total_zone = df_cadres.groupby('Zone').size()

# Nombre d'arrêts par zone (tir cadré non marqué)
saves_zone = df_cadres[df_cadres['Goal'] == 0].groupby('Zone').size()

# Pourcentage d'arrêts
save_pct = (saves_zone / total_zone * 100).fillna(0)

# S'assurer que les 9 zones apparaissent
save_pct = save_pct.reindex(range(1, 10), fill_value=0)

plt.figure(figsize=(10, 5))
plt.bar([str(i) for i in range(1, 10)], save_pct)
plt.xlabel("Zone")
plt.ylabel("Pourcentage d'arrêts (%)")
plt.title("Pourcentage d'arrêts du gardien selon la zone")

for i, value in enumerate(save_pct):
    plt.text(i, value + 0.5, f"{value:.1f}%", ha='center')

plt.show()


# ============================================================
# 1. Equipe qui tire en premier vs équipe qui tire en second
# ============================================================
first_team = (
    df.sort_values(['Game_id', 'Penalty_Number'])
    .groupby('Game_id')
    .first()['Team']
)

df['First_Shooter'] = df['Game_id'].map(first_team)

df['Shoot_Order'] = df.apply(
    lambda row: 'First Team'
    if row['Team'] == row['First_Shooter']
    else 'Second Team',
    axis=1
)

success_rate = (
    df.groupby('Shoot_Order')['Goal']
    .mean() * 100
)

plt.figure(figsize=(6, 5))
success_rate.plot(kind='bar')
plt.ylabel('Scoring percentage (%)')
plt.xlabel('')
plt.title('Success rate: First Team vs Second Team')
plt.xticks(rotation=0)
plt.show()

print("\nSuccess rate (%)")
print(success_rate)


# ============================================================
# 2. Influence du score avant le tir
# ============================================================
df = df.sort_values(['Game_id', 'Penalty_Number']).copy()

pressure_states = []

for game_id, game in df.groupby('Game_id'):

    teams = game['Team'].unique()
    score = {team: 0 for team in teams}

    for idx, row in game.iterrows():

        current_team = row['Team']
        other_team = [t for t in teams if t != current_team][0]

        if score[current_team] > score[other_team]:
            pressure_states.append('Leading')
        elif score[current_team] < score[other_team]:
            pressure_states.append('Trailing')
        else:
            pressure_states.append('Tied')

        if row['Goal'] == 1:
            score[current_team] += 1

df['Score_State'] = pressure_states


# ============================================================
# Taux de réussite selon le contexte psychologique
# ============================================================
pressure_success = (
    df.groupby('Score_State')['Goal']
    .mean() * 100
)

print("\nSuccess rate by game situation (%)")
print(pressure_success)

plt.figure(figsize=(7, 5))
order = ['Leading', 'Tied', 'Trailing']
pressure_success = pressure_success.reindex(order)
pressure_success.plot(kind='bar')
plt.ylabel('Scoring percentage (%)')
plt.xlabel('')
plt.title('Success rate according to score situation')
plt.xticks(rotation=0)
plt.show()


# ============================================================
# Nombre de penalties dans chaque situation
# ============================================================
print("\nNumber of penalties by situation")
print(df['Score_State'].value_counts())


# ============================================================
# 3. NOUVEAU : Heatmap 3x3 du taux de réussite par zone
#              (droitiers vs gauchers)
#   - Figure 1 : TOUS les tirs (inclut les tirs hors cadre)
#   - Figure 2 : tirs CADRÉS uniquement
#   Les deux pour pouvoir comparer.
# ============================================================
# La cage vue comme une grille, d'après la numérotation réelle du CSV :
#   1 2 3   (haut)
#   4 5 6   (milieu)
#   7 8 9   (bas)
zone_layout = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]


def zone_matrices(data):
    """Renvoie (taux de réussite %, nombre de tirs) en grilles 3x3 par zone."""
    goal_rate = data.groupby('Zone')['Goal'].mean().mul(100)
    counts = data.groupby('Zone').size()
    rate = np.array([
        [goal_rate.get(z, np.nan) for z in row]
        for row in zone_layout
    ])
    n = np.array([
        [int(counts.get(z, 0)) for z in row]
        for row in zone_layout
    ])
    return rate, n


def build_annotations(rate, n):
    """Annotation '12.5%\\n(n=8)' par case ; vide si aucun tir."""
    annot = np.empty(rate.shape, dtype=object)
    for i in range(rate.shape[0]):
        for j in range(rate.shape[1]):
            if n[i, j] == 0:
                annot[i, j] = ""
            else:
                annot[i, j] = f"{rate[i, j]:.1f}%\n(n={n[i, j]})"
    return annot


def plot_zone_heatmaps(data_droitier, data_gaucher, suptitle):
    """Trace côte à côte les heatmaps droitiers / gauchers pour un jeu donné."""
    rate_d, n_d = zone_matrices(data_droitier)
    rate_g, n_g = zone_matrices(data_gaucher)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Même échelle de couleur sur les deux pour pouvoir les comparer
    vmin = np.nanmin([rate_d, rate_g])
    vmax = np.nanmax([rate_d, rate_g])

    for ax, rate, n, titre in zip(
        axes,
        [rate_d, rate_g],
        [n_d, n_g],
        ['Droitiers', 'Gauchers']
    ):
        sns.heatmap(
            rate,
            annot=build_annotations(rate, n),
            fmt='',                  # annotations déjà formatées en texte
            cmap='RdYlGn',           # rouge = peu efficace, vert = très efficace
            vmin=vmin,
            vmax=vmax,
            cbar_kws={'label': 'Taux de réussite (%)'},
            xticklabels=['Gauche', 'Centre', 'Droite'],
            yticklabels=['Haut', 'Milieu', 'Bas'],
            linewidths=1,
            linecolor='white',
            ax=ax,
        )
        ax.set_title(
            f'{titre} (total {n.sum()} tirs)',
            fontweight='bold'
        )

    fig.suptitle(suptitle, fontweight='bold', fontsize=13)
    plt.tight_layout()
    plt.show()


# Figure 1 : tous les tirs (version d'origine)
plot_zone_heatmaps(
    df_droitier,
    df_gaucher,
    'Taux de réussite par zone — TOUS les tirs'
)

# Figure 2 : tirs cadrés uniquement
df_droitier_cadre = df_droitier[df_droitier['OnTarget'] == 1]
df_gaucher_cadre = df_gaucher[df_gaucher['OnTarget'] == 1]

plot_zone_heatmaps(
    df_droitier_cadre,
    df_gaucher_cadre,
    'Taux de réussite par zone — TIRS CADRÉS uniquement'
)


# ============================================================
# 4. NOUVEAU : Le gardien part-il du bon côté ?
# ============================================================
# On compare la direction du plongeon (Keeper : L/C/R) avec le côté du tir
# (Area : 1=Left, 2=Middle, 3=Right). Analyse sur les tirs cadrés.
keeper_to_area = {'L': 1, 'C': 2, 'R': 3}

df_keeper = df_cadres.copy()
df_keeper['Keeper_Area'] = df_keeper['Keeper'].map(keeper_to_area)

# Le gardien a-t-il choisi le bon côté ?
df_keeper['Bon_Cote'] = np.where(
    df_keeper['Keeper_Area'] == df_keeper['Area'],
    'Bon côté',
    'Mauvais côté'
)

# Taux d'arrêt = part des tirs NON marqués
save_rate_keeper = (
    df_keeper.groupby('Bon_Cote')['Goal']
    .apply(lambda g: (1 - g.mean()) * 100)
    .reindex(['Bon côté', 'Mauvais côté'])
)

print("\nTaux d'arrêt selon la direction du plongeon (%)")
print(save_rate_keeper)

plt.figure(figsize=(6, 5))
save_rate_keeper.plot(kind='bar', color=['#2a9d8f', '#e76f51'])
plt.ylabel("Pourcentage d'arrêts (%)")
plt.xlabel('')
plt.title("Efficacité du gardien selon la direction du plongeon")
plt.xticks(rotation=0)
for i, value in enumerate(save_rate_keeper):
    plt.text(i, value + 0.5, f"{value:.1f}%", ha='center')
plt.show()


# ============================================================
# 5. NOUVEAU : Pression - taux de réussite par numéro de tir
#               et sur les tirs décisifs (Elimination)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# (a) Taux de réussite par numéro de tir
success_by_number = df.groupby('Penalty_Number')['Goal'].mean().mul(100)

axes[0].plot(
    success_by_number.index,
    success_by_number.values,
    marker='o'
)
axes[0].set_xlabel('Numéro du tir dans la séance')
axes[0].set_ylabel('Taux de réussite (%)')
axes[0].set_title('La pression monte-t-elle avec le numéro de tir ?')
axes[0].grid(alpha=0.3)

# (b) Tirs décisifs vs tirs normaux
elim_success = df.groupby('Elimination')['Goal'].mean().mul(100)
elim_success.index = ['Tir normal', 'Tir décisif']

elim_success.plot(kind='bar', ax=axes[1], color=['#457b9d', '#e63946'])
axes[1].set_ylabel('Taux de réussite (%)')
axes[1].set_xlabel('')
axes[1].set_title('Réussite : tir décisif vs tir normal')
axes[1].tick_params(axis='x', rotation=0)
for i, value in enumerate(elim_success):
    axes[1].text(i, value + 0.5, f"{value:.1f}%", ha='center')

plt.tight_layout()
plt.show()

print("\nTaux de réussite par numéro de tir (%)")
print(success_by_number)
print("\nTaux de réussite tir normal vs décisif (%)")
print(elim_success)


# ============================================================
# 6. NOUVEAU : Taux de réussite par poste
# ============================================================
poste_labels = {'A': 'Attaquant', 'M': 'Milieu', 'D': 'Défenseur'}

poste_stats = df.groupby('Poste')['Goal'].agg(['mean', 'count'])
poste_stats['mean'] = poste_stats['mean'] * 100
poste_stats = poste_stats.rename(index=poste_labels)

print("\nTaux de réussite et nombre de tirs par poste")
print(poste_stats)

plt.figure(figsize=(7, 5))
bars = plt.bar(
    poste_stats.index,
    poste_stats['mean'],
    color='#6a4c93'
)
plt.ylabel('Taux de réussite (%)')
plt.xlabel('')
plt.title('Taux de réussite selon le poste du tireur')

# On affiche le % et le nombre de tirs (effectif) au-dessus de chaque barre
for bar, (_, row) in zip(bars, poste_stats.iterrows()):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"{row['mean']:.1f}%\n(n={int(row['count'])})",
        ha='center'
    )

plt.show()
