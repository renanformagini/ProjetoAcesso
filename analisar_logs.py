import pandas as pd
import sqlite3

def analisar_logs():
    conn = sqlite3.connect('data.db')
    
    df = pd.read_sql_query("SELECT * FROM acessos", conn)

    df['data_hora'] = pd.to_datetime(df['data_hora'])
    df['data'] = df['data_hora'].dt.date

    resumo_dia = df.groupby(['data', 'tipo']).size().unstack(fill_value=0)
    print(resumo_dia)

    colaborador_id = 1  
    tempo_colaborador = df[df['colaborador_id'] == colaborador_id]
    total_horas = tempo_colaborador['data_hora'].diff().dt.total_seconds().sum() / 3600
    print(f"Total de horas do colaborador {colaborador_id}: {total_horas:.2f} horas")

    conn.close()

if __name__ == "__main__":
    analisar_logs()
