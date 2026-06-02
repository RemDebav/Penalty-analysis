import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Utilisez un "r" avant les guillemets pour éviter les problèmes de slashs Windows
df = pd.read_csv(r'c:\Users\remde\Documents\test\WorldCupShootouts.csv')



print(df.head())


# Penalty Shootouts Analysis
def get_area(zone):
    if zone == 1 or zone == 4 or zone == 7:
        return 1
    elif zone == 2 or zone == 5 or zone == 8:
        return 2
    elif zone == 3 or zone == 6 or zone == 9:
        return 3
    else:
        return 0

df['Area'] = df['Zone'].apply(get_area)
print(df.head())
df_droitier= df[df['Foot'] == 'R'].copy()
df_gaucher=df[df['Foot'] == 'L'].copy()
df_hors_cadre = df.copy()

df_hors_cadre = df.copy()

df_hors_cadre.loc[df_hors_cadre['OnTarget'] == 0, 'Area'] = 0

# Calcul des pourcentages par pied
df_pct = df.groupby('Foot')['Area'].value_counts(normalize=True).mul(100).rename('Percentage').reset_index()
#value_counts(normalize=True).mul(100)  transforme les comptes en pourcentages, et barplot à la place de
#countplot pour afficher ces pourcentages sur l'axe Y.


sns.barplot(x='Foot', y='Percentage', hue='Area', data=df_pct)
plt.xlabel('Pied')
plt.ylabel('Pourcentage (%)')
plt.title('Zone préférée selon le pied')
plt.legend(title='Zone')
plt.show()

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Droitiers
goals = df_droitier[df_droitier['Goal'] == 1].groupby('Area').size()

axes[1].pie(
    goals,
    labels=['Left', 'Middle', 'Right'],
    autopct='%1.1f%%'
)
axes[0].set_title('Droitiers', fontweight='bold')

# Gauchers
goals = df_gaucher[df_gaucher['Goal'] == 1].groupby('Area').size()

axes[0].pie(
    goals,
    labels=['Left', 'Middle', 'Right'],
    autopct='%1.1f%%'
)
axes[1].set_title('Gauchers', fontweight='bold')

plt.show()


# Tirs cadrés uniquement
df_cadres = df_hors_cadre[df_hors_cadre['OnTarget'] == 1]

# Nombre total de tirs cadrés par zone
total_zone = df_cadres.groupby('Zone').size()

# Nombre d'arrêts par zone
saves_zone = df_cadres[df_cadres['Goal'] == 0].groupby('Zone').size()

# Pourcentage d'arrêts
save_pct = (saves_zone / total_zone * 100).fillna(0)

# S'assurer que les 9 zones apparaissent
save_pct = save_pct.reindex(range(1, 10), fill_value=0)

plt.figure(figsize=(10,5))

plt.bar(
    [str(i) for i in range(1,10)],
    save_pct
)

plt.xlabel("Zone")
plt.ylabel("Pourcentage d'arrêts (%)")
plt.title("Pourcentage d'arrêts du gardien selon la zone")

for i, value in enumerate(save_pct):
    plt.text(i, value + 0.5, f"{value:.1f}%", ha='center')

plt.show()
