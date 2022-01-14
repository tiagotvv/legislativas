import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.ticker import PercentFormatter


st.title('Eleições Legislativas 2022')

DETAILED_URL = ('./detailed_district.csv')
TOTAL_URL = ('./sim_df.csv')
POLLS_URL = ('./polls_agreg.csv')

@st.cache
def load_data():
    detailed = pd.read_csv(DETAILED_URL)
    total = pd.read_csv(TOTAL_URL)
    polls = pd.read_csv(POLLS_URL)
    return detailed, total, polls

def dHondt(votes, seats):
    num_parties = len(votes)
    quotient = votes
    allocation = np.ones(num_parties)
    while seats > 0:
        quotient = votes/allocation
        idx = np.argmax(quotient)
        allocation[idx] = allocation[idx]+1
        seats = seats - 1
    return allocation-1

data_load_state = st.text('Loading data...')
detailed_district, sim_df, polls = load_data()
data_load_state.text('Loading data... done!')

option = st.selectbox(
     'Escolha uma das opções:',
     ('Início','Sondagens e Resultados', 'Partidos e Coligações', 'Circulos Eleitorais'))

#st.write('Tópico:', option)

u=sim_df.quantile([0.025,0.975]).astype(int).T
#u2019 = [79,108,5,19,12,4,1,1,1]
#v, _ = allocate_seats(votes[:-1])


#u[0.5] = v.astype(int)
#u['vs 2019'] = u[0.5]-u2019

cols = u.columns.tolist()
cols[0] = 'inf'
cols[1] = 'sup'
u.columns = cols
#cols = [cols[i] for i in [0,3,1,2]]
#u = u[u.columns[[0,3,1,2]]]
u = u.sort_values(by=['inf','sup'],ascending=False)
for p in sim_df.columns:
    if (u.loc[p,'inf'])==(u.loc[p,'sup']):
        u.loc[p,'ic'] = str(u.loc[p,'sup'])
    else:
        u.loc[p,'ic'] = str(u.loc[p,'inf'])+"-"+str(u.loc[p,'sup'])  
sorted_parties = u.index


if option == 'Início':

    st.write('Nesta página encontram-se algumas análises realizadas nos resultados de 10000 simulações do ato eleitoral. \
    As simulações usam como ponto de partida um agregado das sondagens mais recentes. \
    As sondagens que compõem este agregado são pesadas de acordo com o número de entrevistas e \
    também de acordo com a data em que foi realizada.')

    st.write('A opção **Sondagens e Resultados** apresenta uma tabela com a lista de sondagens utilizadas\
    pelo simulador e também apresenta os resultados globais e a distribuição dos mandatos nos círculos eleitorais')

    st.write('Na opção **Partidos e Coligaçóes** é poss+ivel ver em detalhes o resultado de um partido individualmente ou criar \
    coligações hipotéticas.')

    st.write('A opção **Círculos Eleitorais** fornece informação detalhada a respeito da probabilidade de um candidato \
    de uma lista partidária ser eleito no círuclo eleitoral em que concorre. Responde perguntas do tipo: "Qual a \
    probabilidade do candidato número 3 da lista do PAN ser eleito no círculo de Lisboa?' )

if option == 'Sondagens e Resultados':

    def inf(x):
        return x.quantile(0.025)

    def sup(x):
        return x.quantile(0.975)

    f = {'PS': [inf, sup],
        'PSD': [inf, sup],
        'Chega': [inf, sup],
        'BE': [inf, sup],
        'CDU': [inf, sup],
        'PAN': [inf, sup],
        'CDS-PP': [inf, sup],
        'IL': [inf, sup],
        'LIVRE': [inf, sup],
        }
    
    dc = {'PS': 'PS',
        'PSD': 'PSD',
        'Chega': 'CHE',
        'BE': 'BE',
        'CDU': 'CDU',
        'PAN': 'PAN',
        'CDS-PP': 'CDS',
        'IL': 'IL',
        'LIVRE': 'L',
        }
    
    
    st.markdown('**Sondagens consideradas**')

    st.write(polls.style.format({'PS': '{:0,.1f}','PSD': '{:0,.1f}',
   'CDS': '{:0,.1f}','BE': '{:0,.1f}', 'CDU': '{:0,.1f}','PAN': '{:0,.1f}',
    'IL': '{:0,.1f}', 'CHE': '{:0,.1f}','L': '{:0,.1f}','OBN': '{:0,.1f}','w_poll': '{:0,.2f}',}))
    zz = polls.loc[0,'Tamanho Amostra']
    st.write('Tamanho da amostra ponderada: ', zz)
    st.write('Margem de erro: ', round(196*math.sqrt(0.25/zz),2),'%')
    #st.write(u.style.format({"vs 2019": "{:+0,.0f}"}))
    
    st.markdown('**Resultados e mandatos**')
    vote = pd.DataFrame()
    for p in sorted_parties:
        vote.loc[p, '% votos'] = polls.loc[0, dc[p]]
        vote.loc[p, 'mandatos'] = u.loc[p,'ic']
    st.write(vote.style.format({'% votos':'{:0,.1f}'}))
    pp=detailed_district.iloc[:,:-1].groupby('circulo').agg(f).astype(int)
    #pp.to_csv('circulos_2019_10_04.csv',sep=',')
    st.markdown('**Distribuição dos mandatos nos círculos eleitorais**')
    dff = pd.DataFrame()
    for c in pp.index:
        for p in sorted_parties:
            if (pp.loc[c][p,'inf'])==(pp.loc[c][p,'sup']):
                dff.loc[c, p] = str(pp.loc[c][p,'sup'])
            else:
                dff.loc[c, p] = str(pp.loc[c][p,'inf'])+"-"+str(pp.loc[c][p,'sup'])
                
    

    for p in sorted_parties:
        if (u.loc[p,'inf'])==(u.loc[p,'sup']):
            dff.loc['Total', p] = str(u.loc[p,'sup'])
        else:
            dff.loc['Total', p] = str(u.loc[p,'inf'])+"-"+str(u.loc[p,'sup'])  
        #dff.loc['Agregado Sondagens', p] =  str(u.loc[p,'med'])
    st.write(dff)

if option == 'Partidos e Coligações':

    def frange(start, stop, step=1):
        i = start
        while i < stop:
            yield i
            i += step 

    colig = []
    string_col = ''

    col1, col2, col3 = st.columns(3)
    ps = col1.checkbox('PS')
    psd = col2.checkbox('PSD')
    cds = col3.checkbox('CDS-PP')
    cdu = col1.checkbox('CDU')
    be = col2.checkbox('BE')
    ch = col3.checkbox('Chega')
    il = col1.checkbox('IL')
    pan = col2.checkbox('PAN')
    livre = col3.checkbox('LIVRE')



    if ps:
        colig.append('PS')
        string_col = string_col + ' PS '
    if psd:
        colig.append('PSD')
        string_col = string_col + ' PSD '
    if cds:
        colig.append('CDS-PP')
        string_col = string_col + ' CDS-PP '
    if cdu:
        colig.append('CDU')
        string_col = string_col + ' CDU '
    if be:
        colig.append('BE')
        string_col = string_col + ' BE '
    if ch:
        colig.append('Chega')
        string_col = string_col + ' Chega '
    if il:
        colig.append('IL')
        string_col = string_col + ' IL '
    if pan:
        colig.append('PAN')
        string_col = string_col + ' PAN '
    if livre:
        colig.append('LIVRE')
        string_col = string_col + ' LIVRE '
    
    num_partidos = ps+psd+cds+cdu+be+ch+il+pan+livre

    coligacao = sim_df[colig].sum(axis=1)
    tick=[]
    lbl = []
    for i in frange(min(coligacao+0.5),max(coligacao+1.5)):
        tick.append(i)
        lbl.append(int(i-0.5))

    prob_maioria = round((coligacao>115).sum()/100,1)
    
    cq = coligacao.quantile([0.025,0.975]).fillna(0).astype(int).T
    cq.columns = [string_col]
    if num_partidos > 0:
        if num_partidos > 1:
            st.markdown('**Partido Selecionado: ' + string_col+"**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Mínimo", cq[0.025], "")
            col2.metric("Máximo", cq[0.975], "")
            col3.metric("Prob de Maioria Absoluta", str(prob_maioria)+'%',"")
            titulo = 'Coligação: '+string_col
        if num_partidos == 1:
           # st.write('O partido ', string_col,' elege entre ', cq[0.025], ' e ', cq[0.975], ' deputados')
           # st.write('O partido tem probabilidade ', prob_maioria, '% de obter maioria absoluta')
            st.markdown('**Partido Selecionado: ' + string_col+"**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Mínimo", cq[0.025], "")
            col2.metric("Máximo", cq[0.975], "")
            col3.metric("Prob de Maioria Absoluta", str(prob_maioria)+'%',"")
            titulo = 'Partido: '+string_col
    
        #plt.ylabel('% de Simulações')
        #plt.xlabel('Número de Assentos')
        fig, ax = plt.subplots()
        ax=coligacao.hist(figsize=(10,2), facecolor = 'gray', alpha=0.7, 
                            bins=range(min(coligacao),max(coligacao+2)), cumulative=0, density=True)
        ax.set_xticks(tick)
        ax.axvline(116, linewidth=4)
        ax.set_xticklabels(lbl,rotation=45)
        ax.set_xlabel('Número de Assentos')
        ax.set_ylabel('% de simulações')
        ax.set_title(titulo)
        #ax.set_xlim(3,20)
        #ax.set_xticks(np.arange(3,21)+0.5)
        #ax.set_xticklabels(range(3,21),rotation=45)
        #ax.set_ylim(0,0.75)
        #ax.grid('off')
        ax.set_xlim(min(tick)-0.5, max(tick)+0.5)
        ax.yaxis.set_major_formatter(PercentFormatter(1))
        st.pyplot(fig)

if option == 'Circulos Eleitorais':
    def HIGHLIGHT_COLOR(x):
        def colour_switch(number):
            if number == '-':
                color = 'white'
            elif number == 100:
                color = "green"
            elif (number >97.5)&(number<100):
                color = "lightgreen"
            elif (number >=2.5)&(number<=97.5):
                color = "#ffff9e"
            elif (number >0)&(number<2.5): 
                color = "#ffffe2"
            elif number == 10:
                color = "black"
            else:
                # default
                color = "white"
                
            return color

        return [f'background-color: {colour_switch(number)}' for number in x]

    circ = st.selectbox(
     'Escolha o Círculo Eleitoral',
     ('Acores', 'Aveiro', 'Beja', 'Braga', 'Braganca', 'Castelo Branco',
       'Coimbra', 'Evora', 'Faro', 'Guarda', 'Leiria', 'Lisboa', 'Madeira',
       'Portalegre', 'Porto', 'Santarem', 'Setubal', 'Viana do Castelo',
       'Vila Real', 'Viseu', 'zExterior - Europa', 'zExterior - Fora Europa'))

    seats = {'Acores':5, 'Aveiro':16, 'Beja':3, 'Braga':19, 'Braganca':3, 'Castelo Branco':4,
       'Coimbra':9, 'Evora':3, 'Faro':9, 'Guarda':3, 'Leiria':10, 'Lisboa':48, 'Madeira':6,
       'Portalegre':2, 'Porto':40, 'Santarem':9, 'Setubal':18, 'Viana do Castelo':6,
       'Vila Real':5, 'Viseu':8, 'zExterior - Europa':2, 'zExterior - Fora Europa':2}
    
    st.markdown("***A tebela é lida da seguinte forma: a entrada na linha N de cada partido é a % \
    de simulações em que o candidato N da lista conseguiu ser eleito.***")
    resultado_partidario = pd.DataFrame()

    for partido in sorted_parties:
        single_district = detailed_district.loc[(detailed_district['circulo'] ==circ), partido].astype(int)
        #single_district.value_counts()/100
        bbb = detailed_district.loc[(detailed_district['circulo'] ==circ), partido].astype(int)
        #max_val = detailed_district.loc[(detailed_district['circulo'] ==circ)].iloc[:,:-3].astype(int).max().max()

        bbb= (round(bbb.astype(pd.api.types.CategoricalDtype(categories=range(25))).value_counts()/100,5)).sort_index()
    
        resultado_partidario[partido] = bbb
    resultado_partidario = resultado_partidario.loc[1:]
     #   resultado_partidario.loc[circ,] = 1
    #display((resultado_partidario[resultado_partidario == 0] ).fillna(''))
    #resultado_partidario = 100-resultado_partidario.cumsum()
    resultado_partidario = round(resultado_partidario[::-1].cumsum()[::-1],1)
    
    st.markdown('**Circulo Selecionado: ' + circ+"**")

    st.write(resultado_partidario[:min(24,seats[circ])].style.apply(HIGHLIGHT_COLOR).format('{:.1f}'))