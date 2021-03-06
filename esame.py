#classe alzata per le eccezioni
class ExamException(Exception):
  pass

class CSVTimeSeriesFile():
  def __init__(self, name):
    # controllo il tipo di name(deve essere str)
    if not isinstance(name, str):
      raise ExamException("name non è una stringa")
    
    # controllo passato
    self.name = name

  #creo un metodo che torni una lista di liste, dove il primo elemento delle liste annidate è la data ed il secondo il numero di passeggeri (consegna)
  def get_data(self):
    # controllo che il file esista
    try:
      # provo ad aprire il file in lettura
      file_csv = open(self.name, 'r')
    except:
      raise ExamException('File non esistente')

    time_series = []

    # analizzo il file
    for line in file_csv:
      #faccio uno split per ottenere un array di elementi (in questo caso considerando la virgola)
        line = line.split(',')
        # controllo che ci siano almeno due elementi(data, numero di passeggeri) anche se ci dovessero essere altri campi non influirebbe
        if len(line) >= 2:
          date = line[0]
          passengers = line[1]
          # controllo che la data contenga l'anno e il mese(formato data --> YY-MM)
          date = date.split('-')
          if len(date) >= 2:
            year = date[0]
            month = date[1]
            # controllo che l'anno, il mese e il numero di passeggeri siano validi
            # controllo la validità del tipo
            try:
              year = int(year)
              month = int(month)
              passengers = int(passengers)
            except:
              continue # interrompo il for e inizio il ciclo successivo (ignoro la riga del csv)
            # l'anno deve essere positivo(consegna), il mese compreso tra 1 e 12
            if year >= 0:
              if 1 <= month <= 12:
                # controllo che il numero di passeggeri sia positivo
                if passengers >= 0:
                  # in questo punto ho tutti i dati che cercavo(data, passeggeri)
                  # controllo che la timeserie sia ordinata e priva di duplicati
                  if len(time_series) > 0:
                    #contollo che ci sia almeno un elemento
                    # prendo la data dell'ultimo elemento inserito nella variabile time_series
                    prev_date = time_series[-1][0]
                    prev_date = prev_date.split('-')
                    prev_year = int(prev_date[0])
                    prev_month = int(prev_date[1])
                    if prev_year <= year:
                        if prev_year == year:
                          if prev_month >= month:
                            raise ExamException("time_series presenta duplicati o non è ordinata")
                    else: 
                      raise ExamException("time_series presenta duplicati o non è ordinata")
                  # passati questi controlli la time_series è priva di duplicati ed è ordinata
                  # aggiungo il time_stamp appena analizzato all'interno di time_series
                  time_series.append([f"{year}-{str(month).zfill(2)}", passengers])  # zfill trasforma '1' in '01' ad esempio

    # chiudo il file
    file_csv.close()
    return time_series

def compute_avg_monthly_difference(time_series, first_year, last_year):
  # assumo di ricevere una time_series corretta
  # controllo validità di tipo dei parametri
  if not isinstance(time_series, list):
    raise ExamException("time_series non è una lista")
  if not isinstance(first_year, str):
    raise ExamException("first_year non è una stringa")
  if not isinstance(last_year, str):
    raise ExamException("last_year non è una stringa")

  # controllo che first_year e last_year siano anni
  try:
    first_year = int(first_year)
    last_year = int(last_year)
  except:
    raise ExamException("Anni non validi")

  if first_year < 0:
    raise ExamException("first_year non valido")
  if last_year < 0:
    raise ExamException("last_year non valido")
  if first_year >= last_year:
    raise ExamException("range di anni non valido")

  # controllo che la time_series sia valida

  first_year = str(first_year)
  last_year = str(last_year)

  # organizzo i dati in modo da poterli reperire più facilmente
  # costruisco un array in questo modo
  # passengers_per_year = [[]
  #   (una lista con altre liste)
  #[["_anno_", [passeggeri_gennaio, passeggeri_di_febbraio,...]],
  #   [["_anno_", [passeggeri_gennaio, passeggeri_di_febbraio,...]],
  #   ...]]
  # se un mese dovesse mancare rimpiazzo con None

  passengers_per_year = []

  for time_stamp in time_series:
    date = time_stamp[0].split('-')
    year = date[0]
    month = int(date[1])
    passengers = time_stamp[1]
    #controllo  se ho già inserito l'anno in passengers_per_year
    #creo con una  list comprehension una lista, dove vado a prendere tutti gli elementi di passengers_per_year (e prendo il primo elemento [0])
    if year in [passengers_list[0] for passengers_list in passengers_per_year]:
      # trovo la posizione dell'anno in time_series, vado a trovare lindice della lista in modo tale da poter prendere il numero di passeggeri per mesi di quell'anno
      i = [passengers_list[0] for passengers_list in passengers_per_year].index(year)
      #Utilizzo la funzione .index che ritorna lindice, cioè la posizione di un elemento all'interno della lista

      # prendo la lista di passeggeri per quell'anno
      passengers_per_month = passengers_per_year[i][1]
      # inserisco il numero di passeggeri nella posizione month - 1
      passengers_per_month[month - 1] = passengers
      # aggiorno passengers_per_year, assegnandoli la lista di passeggeeri per ogni mese modificata
      passengers_per_year[i][1] = passengers_per_month
    else:
      #se lanno non è presente
      # inizializzo una lista di 12 elementi con None di default
      passengers_per_month = [None for i in range(0,12)]
      # inserisco il numero di passeggeri nella posizione month - 1
      passengers_per_month[month - 1] = passengers
      # aggiorno passengers_per_year, faccio un append perchè la lista non è ancora presente in passengers_per_year
      passengers_per_year.append([year, passengers_per_month])

  # controllo che gli anni siano all'interno della time_series
  #prendo tutti gli anni tramite list comprehension
  years_list = [item[0] for item in passengers_per_year]
  if not (first_year in years_list and last_year in years_list):
    raise ExamException("Anni non contenuti nella time series")

  # calcolo media
  #creo una lista che ritornerà i nostri 12 risultati
  result = []
  for i in range(0,12):
    # prendo tutti i passeggeri di tutti gli anni in un mese specifico
    passengers_per_month = []
    for line in passengers_per_year:
      year = line[0]
      # controllo che l'anno considerato sia contenuto tra first_year e last_year(poichè la media va calcolata tra essi)
      if int(first_year) <= int(year) <= int(last_year):
        # prendo i passeggeri del mese i
        passengers = line[1][i]
        passengers_per_month.append(passengers)
    # sommo le differenze tra i vari anni
    sum = 0
    value_to_divide = 0  # contatore per calcolare quanti valori sono considerati nella media, importante perchè ci possono essere dei valori none che dovremo scartare
    for j in range(0, len(passengers_per_month)):
      if j != 0:
        if passengers_per_month[j] != None and passengers_per_month[j - 1] != None:
          sum += (passengers_per_month[j] - passengers_per_month[j - 1])
          value_to_divide += 1
    # mi accerto di non dividere per 0
    if value_to_divide == 0:
      # in questo caso non avevo abbastanza valori per fare la media
      result.append(0)
    else:
      result.append(sum / value_to_divide)
    
  return result

