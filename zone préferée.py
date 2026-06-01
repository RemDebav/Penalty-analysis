import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv(r'C:\Users\RaidMABROUK\OneDrive\Desktop\data\WorldCupShootouts.csv')

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