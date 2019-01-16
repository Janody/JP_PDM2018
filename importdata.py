
import pandas as pd
import data_utils as du

def importPed(filepath, start, end, direct = True, calib = True):

    #Importe les comptages piétons pour la période spécifiée
    #filepath: adresse du fichier
    #start: début de la période
    #end: fin de la période
    #direct: comptages directionnels présents, si Vrai, garde les valeurs directionnelles, sinon uniquement Total
    #calib: applique le calibrage

    data = pd.read_csv(filepath, sep=';')
    data['Date'] = pd.to_datetime(data.Date, dayfirst=True)

    if 'Ville de Pully_1' in data.columns: #Nom donné aux anciens compteurs
        name1 = 'Ville de Pully_1'
        name2 = 'Ville de Pully_2'

    elif 'Trottoir Nord Rue de la Poste' in data.columns: #Nom donné aux nouveaux compteurs
        name1 = 'Trottoir Nord Rue de la Poste'
        name2 = 'Trottoir Sud Rue de la Poste'

    else:
        raise ValueError('Vérifier les noms des compteurs')

    # selection de la bonne période de travail
    mask = (data['Date']>= start) & (data['Date']<=end)
    data = data.loc[mask]
    data.reset_index(inplace = True)

    #application du calibrage
    calib1 = du.calibrage(data[name1])
    calib2 = du.calibrage(data[name2])

    if calib:
        data[name1] = pd.Series(calib1)
        data[name2] = pd.Series(calib2)

    #ajout de paramètres (jours de la semaine, heures etc.)
    data['Total'] = data[[name1,name2]].sum(axis=1)
    data['days'] = data['Date'].dt.strftime("%d/%m")
    data['hours'] = data['Date'].dt.strftime("%H")
    data['DayWeek'] = data['Date'].dt.strftime("%a")

    #suppression des comptages directionnels si besoin
    if direct == False:
        data.drop(name1, axis=1, inplace=True)
        data.drop(name2, axis=1, inplace=True)
        data.reset_index(drop=True, inplace=True)
        data = data[['Date','days', 'DayWeek', 'hours', 'Total']]
    else:
        data.reset_index(drop=True, inplace=True)
        data = data[['Date','days', 'DayWeek', 'hours',name1, name2, 'Total']]

    return data

def importVeh(filepath, start, end):
    # importe les comptages véhicules pour la période spécifiée
    # filepath: adresse du fichier
    # start: début de la période (variable de type datetime)
    # end: fin de la période (variable de type datetime)

    data = pd.read_csv(filepath, sep=';')
    if 'Date-heure' in data.columns:
        data['Date-Heure'] = pd.to_datetime(data['Date-Heure'], dayfirst=True) #attention aux noms des colonnes
        mask = (data['Date-Heure'] >= start) & (data['Date-Heure'] <= end)
        data = data.loc[mask]
    else:
        raise ValueError('Vérifier que le nom de la colonne "Date" soit bien "Date-Heure"' )

    #changement de nom de la colonne
    data.set_axis(['Date', 'Total'], axis =1, inplace = True)

    #ajout de paramètres (jours de la semaine, heures etc.)
    data['days'] = data['Date'].dt.strftime("%d/%m")
    data['hours'] = data['Date'].dt.strftime("%H")
    data['DayWeek'] = data['Date'].dt.strftime("%a")

    #mise en forme du tableau
    data.reset_index(drop=True, inplace=True)
    data = data[['Date', 'days', 'DayWeek', 'hours', 'Total']]

    return data

def importSC(filepath, start,end, mode = False):
    # importe les statistiques swisscom pour la période sélectionnée
    # filepath: adresse du fichier
    # start: début de la période (variable de type datetime)
    # end: fin de la période (variable de type datetime)
    # mode: le fichier téléchargé correspond à des débits par modes (par défaut: débits par type Transit, Inward...)

    data = pd.read_csv(filepath, sep=',', header=None, index_col=0,skiprows =1)
    data = data.T #transposition du tableau pour garder la même mise en forme que les autres
    data['Date'] = pd.to_datetime(data.Date, format='%Y-%m-%dT%H') #transformation de la colonne date dans le bon format

    #sélection de la bonne période de travail
    mask = (data['Date'] >= start) & (data['Date'] <= end)
    data = data.loc[mask]

    data['Total'] = data['Total'].astype(str).astype(int).copy() #transformation de la colonne total dans le bon format

    if mode == True:
        #transformation dans le bon format
        if 'Road' in data.columns:
            data['Road'] = data['Road'].astype(str).astype(int).copy()
        if 'Train' in data.columns:
            data['Train']=  data['Train'].astype(str).astype(int).copy()

        if 'Highway' in data.columns:
            data['Highway']= data['Highway'].astype(str).astype(int).copy()

    data['days'] = data['Date'].dt.strftime("%d/%m")
    data['hours'] = data['Date'].dt.strftime("%H")
    data['DayWeek'] = data['Date'].dt.strftime("%a")
    data.reset_index(drop=True, inplace=True)

    if mode == False:
        #on conserve juste le total
        #attention: enlever cette partie si on veut faire une étude spécifique par types de trajet
        if 'Transit' in data.columns:
            data.drop('Transit', axis=1, inplace=True)

        if 'Outward' in data.columns:
            data.drop('Outward', axis=1, inplace=True)

        if 'Inward' in data.columns:
            data.drop('Inward', axis=1, inplace=True)

        if 'Local' in data.columns:
            data.drop('Local', axis=1, inplace=True)

        data = data[['Date','days', 'DayWeek', 'hours', 'Total']]

    return data



def importTL(filepath,start,end, sheet):
    # importe les statistiques TL pour la période sélectionnée
    # filepath: adresse du fichier (EXCEL)
    # start: début de la période (variable de type datetime)
    # end: fin de la période (variable de type datetime)
    # sheet: feuille du fichier excel dans laquelle se trouvent les débits


    df = pd.read_excel(filepath, sheet_name=sheet)

    #sélection de la bonne période de travail et du bon arrêt
    df['Jour de Date Exploitation'] = pd.to_datetime(df['Jour de Date Exploitation'])
    mask_arret = (df['Arret Libelle'] == 'Pully, Centre')
    mask_date = (df['Jour de Date Exploitation'] >= start) & (df['Jour de Date Exploitation'] <= end)
    mask_arret2 = (df['arret fin libelle parcours principal'] != 'Pully, Centre')
    df = df.loc[mask_arret]
    df = df.loc[mask_arret2]
    df = df.loc[mask_date]

    #mise en forme
    df.rename(columns={'Jour de Date Exploitation': 'Date', 'A Bord Final': 'Total', 'Tranche hh:mm depart': 'Heure'},
                inplace=True)
    df['Heure'] = [x.hour for x in df.Heure]
    df = df[['Date', 'Heure', 'Total']]

    data = df.groupby(['Date', 'Heure']).sum() #groupement des valeurs par date et heure
    data = data.reset_index()

    # mise en forme de la date pour que ça matche avec les autres sources
    data['Date2'] = pd.to_datetime(data.Date) + pd.to_timedelta(data.Heure, unit='h')
    data.drop('Heure', axis=1, inplace=True)
    data.drop('Date', axis=1, inplace=True)
    data = data[['Date2', 'Total']]
    data.rename(columns={'Date2': 'Date'}, inplace=True)

    dates = pd.date_range(start, end, freq='H', closed=None, name='Date')
    data= data.set_index(['Date']).reindex(dates, fill_value=0).reset_index()

    # ajout de paramètres (jours de la semaine, heures etc.)
    data['days'] = data['Date'].dt.strftime("%d/%m")
    data['hours'] = data['Date'].dt.strftime("%H")
    data['DayWeek'] = data['Date'].dt.strftime("%a")

    #mise en forme du tableau
    data = data[['Date', 'days', 'DayWeek', 'hours', 'Total']]

    return data


