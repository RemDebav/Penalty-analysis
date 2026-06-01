import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Utilisez un "r" avant les guillemets pour éviter les problèmes de slashs Windows
df = pd.read_csv(r'c:\Users\remde\Documents\test\WorldCupShootouts.csv')



print(df.head())


# Penalty Shootouts Analysis
def get_area(zone):
    if zone in [1, 4, 7]:
        return 1
    elif zone in [2, 5, 8]:
        return 2
    elif zone in [3, 6, 9]:
        return 3

df['Area'] = df['Zone'].apply(get_area)

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

# On améliore en mettant en fréquence
# 1. Création de la figure avec 1 ligne et 2 colonnes
# figsize=(15, 6) permet de donner assez de largeur pour les deux
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# 2. Premier graphique (Droitiers) sur l'axe 0 (gauche)
sns.countplot(x='Foot', hue='Area', data=df_droitier, ax=axes[0])
axes[0].set_title('Zones préférées : Droitiers')
axes[0].set_xlabel('Pied (R)')
axes[0].set_ylabel('Nombre de tirs')

# 3. Deuxième graphique (Gauchers) sur l'axe 1 (droite)
sns.countplot(x='Foot', hue='Area', data=df_gaucher, ax=axes[1])
axes[1].set_title('Zones préférées : Gauchers')
axes[1].set_xlabel('Pied (L)')
axes[1].set_ylabel('Nombre de tirs')

# Ajuste automatiquement l'espacement pour éviter que les titres se chevauchent
plt.tight_layout()
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
