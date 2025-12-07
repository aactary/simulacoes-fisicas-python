# Projeto: Simulações de Física com Python
# Autor: Ari Cardoso
# Licença: GNU General Public License v3.0
#
# Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
# sob os termos da Licença Pública Geral GNU conforme publicada pela Free Software Foundation,
# na versão 3 da licença.
#
# Este programa é distribuído na esperança de que seja útil,
# mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
# COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO PROPÓSITO.
# Veja a Licença Pública Geral GNU para mais detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa. Se não, veja <https://www.gnu.org/licenses/>.

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from django.template import loader
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objects as go

def index(request):
    return render(request, 'simulacoes/index.html', {})

def simulacao_projetil(request):
    # valores padrão
    velocidade = 20
    angulo = 45
    gravidade = 9.8

    if request.method == 'GET':
        # atualiza os parametros
        velocidade = float(request.GET.get('velocidade', velocidade))
        angulo = float(request.GET.get('angulo', angulo))
        gravidade = float(request.GET.get('gravidade', gravidade))

    # calculos da física
    angulo_rad = np.radians(angulo)
    tempo_total = 2 * velocidade * np.sin(angulo_rad) / gravidade
    # Alcance (distância total)
    alcance = (velocidade ** 2 * np.sin(2 * angulo_rad)) / gravidade
    
    # Altura máxima
    altura_maxima = (velocidade ** 2 * (np.sin(angulo_rad) ** 2) / (2 * gravidade))
    tempos = np.linspace(0, tempo_total, 100)
    x = velocidade * np.cos(angulo_rad) * tempos
    y = velocidade * np.sin(angulo_rad) * tempos - 0.5 * gravidade * tempos**2

    fig = gerar_grafico_plotly(x, y, velocidade, angulo, gravidade)
    html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    #prepara resposta
    context = {
        'imagem_grafico': html,
        'velocidade': velocidade,
        'angulo': angulo,
        'gravidade': gravidade,
        'alcance': f"{alcance:.3f}",
        'altura_maxima': f"{altura_maxima:.3f}",
        'tempo_total': f"{tempo_total:.3f}",
    }

    template = loader.get_template('simulacoes/simulacao_projetil.html')
    return HttpResponse(template.render(context, request))

def curva_aquecimento(request):
    # valores padrão
    massa = 100
    T0 = -20
    Tf = 120
    if request.method == 'GET':
        massa = float(request.GET.get('massa', massa))  # em gramas
        T0 = float(request.GET.get('temp_inicial', T0))  # em °C
        Tf = float(request.GET.get('temp_final', Tf))    # em °C

    # Constantes
    c_ice = 2.1     # J/g°C
    c_water = 4.18
    c_steam = 2.0
    Lf = 334        # J/g
    Lv = 2260       # J/g

    temp = []
    calor = []
    labels = []
    Q = 0

    # Etapas
    if T0 < 0:
        t1 = list(range(int(T0), 1))
        q1 = [massa * c_ice * (t - T0) for t in t1]
        q1 = [Q + q for q in q1]
        Q = q1[-1]
        temp += t1
        calor += q1
        labels += ['Sensível (Gelo)'] * len(t1)

    if T0 <= 0 < Tf:
        temp += [0, 0]
        calor += [Q, Q + massa * Lf]
        Q = calor[-1]
        labels += ['Latente (Fusão)'] * 2

    if T0 <= 0 < Tf:
        t3 = list(range(1, min(101, int(Tf) + 1)))
        q3 = [Q + massa * c_water * (t - 0) for t in t3]
        Q = q3[-1] if q3 else Q
        temp += t3
        calor += q3
        labels += ['Sensível (Líquido)'] * len(t3)

    if Tf > 100:
        temp += [100, 100]
        calor += [Q, Q + massa * Lv]
        Q = calor[-1]
        labels += ['Latente (Vaporização)'] * 2

        t5 = list(range(101, int(Tf) + 1))
        q5 = [Q + massa * c_steam * (t - 100) for t in t5]
        temp += t5
        calor += q5
        labels += ['Sensível (Vapor)'] * len(t5)

    # Gráfico
    sns.set(style='whitegrid', palette='muted')
    plt.figure(figsize=(10, 6))

    colors = {
        'Sensível (Gelo)': '#1f77b4',
        'Latente (Fusão)': '#ff7f0e',
        'Sensível (Líquido)': '#2ca02c',
        'Latente (Vaporização)': '#d62728',
        'Sensível (Vapor)': '#9467bd'
    }

    for stage in set(labels):
        indices = [i for i, label in enumerate(labels) if label == stage]
        plt.plot([temp[i] for i in indices], [calor[i] for i in indices],
                    label=stage, color=colors[stage], linewidth=2)

    plt.xlabel("Temperatura (°C)")
    plt.ylabel("Calor (J)")
    plt.title("Curva de Aquecimento da Água")
    plt.legend(title="Tipo de Calor")
    plt.tight_layout()

    # Converter para base64
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    imagem_grafico = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    context = {
        'simulation':{
            'title': 'Curva de Aquecimento da Água',
            'category': 'Termodinâmica',
            'description': '',
        },
        'imagem_grafico': imagem_grafico,
        'massa': massa,
        'temp_inicial': T0,
        'temp_final': Tf,
        'energia_total': round(Q, 2)  # total em J
    }
    template = loader.get_template('simulacoes/curva_aquecimento.html')
    return HttpResponse(template.render(context, request))

def dilatacao_termica(request):

    # Parâmetros físicos
    L0 = 1.0              # comprimento inicial (m)
    alpha = 12e-6        # coeficiente de dilatação linear
    T0 = 20               # temperatura inicial (°C)
    Tmax = 300            # temperatura final (°C)
    passos = 50           # número de quadros
    alpha_input = 0

    if request.method == 'GET':
        # atualiza os parametros
        if request.GET.get('coeficiente'):
            alpha = float(request.GET.get('coeficiente', alpha))
            alpha_input = float(request.GET.get('coeficiente', alpha))
            alpha = alpha * 10**-6
        else:
            alpha_input =  alpha / 10**-6

        L0 = float(request.GET.get('comprimento', L0))
        T0 = float(request.GET.get('temp_inicial', T0))
        Tmax = float(request.GET.get('temp_final', Tmax))
        

    temperaturas = np.linspace(T0, Tmax, passos)
    comprimentos = L0 * (1 + alpha * (temperaturas - T0))

    # Frames: barra cinza (L0) e parte dilatada (vermelho)
    frames = []
    for i in range(passos):
        T = temperaturas[i]
        L = comprimentos[i]
        delta_L = L - L0

        trace_fixo = go.Scatter(x=[0, L0], y=[0, 0], mode='lines',
                                line=dict(color='black', width=12),
                                hoverinfo='skip', showlegend=False)
        trace_dilatado = go.Scatter(x=[L0, L], y=[0, 0], mode='lines',
                                    line=dict(color='red', width=12),
                                    text=[f"T = {T:.1f} °C<br>ΔL = {delta_L:.5f} m<br>L = {L:.5f} m"],
                                    hoverinfo='text', showlegend=False)
        frames.append(go.Frame(data=[trace_fixo, trace_dilatado], name=str(i)))

    # Slider (barra de controle)
    slider_steps = [
        dict(method="animate",
            args=[[str(i)],
                {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}],
            label=f"{temperaturas[i]:.0f}°C")
        for i in range(passos)
    ]

    sliders = [dict(
        active=0,
        pad={"t": 30, "b": 0},
        steps=slider_steps,
        x=0.12, y=0.05,  # centraliza horizontalmente
        len=0.85,
        currentvalue={"prefix": "Temperatura: ", "xanchor": "right"},
    )]

    # Botões Play/Pause alinhados com o slider (mesma altura: y=0.05)
    buttons = [dict(
        type="buttons",
        direction="left",
        x=0.1, y=-0.18,
        showactive=False,
        buttons=[
            dict(label="▶", method="animate",
                args=[None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}]),
            dict(label="⏸", method="animate",
                args=[[None], {"frame": {"duration": 0}, "mode": "immediate", "transition": {"duration": 0}}])
        ]
    )]

    # Criação da figura inicial
    fig = go.Figure(
        data=[
            go.Scatter(x=[0, L0], y=[0, 0], mode='lines',
                    line=dict(color='gray', width=12), showlegend=False),
            go.Scatter(x=[L0, comprimentos[0]], y=[0, 0], mode='lines',
                    line=dict(color='red', width=12),
                    text=[f"T = {temperaturas[0]:.1f} °C<br>ΔL = {(comprimentos[0]-L0):.5f} m<br>L = {comprimentos[0]:.5f} m"],
                    hoverinfo='text', showlegend=False)
        ],
        layout=go.Layout(
            # title="Dilatação Térmica de uma Barra Metálica",
            xaxis=dict(title="Comprimento (m)", range=[-0.05, comprimentos[-1] + 0.05]),
            yaxis=dict(visible=False),
            height=400,
            margin=dict(t=50, b=100),
            sliders=sliders,
            updatemenus=buttons
        ),
        frames=frames
    )
    
    grafico_dilatacao = fig.to_html(full_html=False, include_plotlyjs='cdn')

    template = loader.get_template('simulacoes/dilatacao_termica.html')
    context = {
        'simulation':{
            'title': 'Dilatação Térmica de uma Barra Metálica',
            'category': 'Termodinâmica',
            'description': '',
        },
        'grafico_dilatacao': grafico_dilatacao,
        't0': T0,
        'tf': temperaturas[-1],
        'delta_L': f"{delta_L:.4f}",  # Formata para 4 casas decimais
        'Lf': f"{comprimentos[-1]:.4f}",  # Formata para 4 casas decimais,
        'L0': L0, 
        'alpha': alpha_input,  
        'T0': T0, 
        'Tmax': Tmax, 
    }
    return HttpResponse(template.render(context, request))

def lei_gravitacao_universal_newton(request):
    # Valores iniciais padrão
    context = {
        'simulation': {
            'title': 'Lei da Gravitação Universal',
            'category': 'Mecânica Celeste',
            'icon': 'globe', # Ícone do Bootstrap
            'description': 'Simule a órbita de corpos celestes alterando massa e velocidade inicial. Observe como a força gravitacional molda as trajetórias circulares, elípticas ou hiperbólicas.',
            'updated_at': '07/12/2025'
        },
        # Parâmetros padrão para os inputs HTML
        'defaults': {
            'massa_sol': 1.0,  # Unidades arbitrárias para facilitar a visualização
            'vel_inicial': 1.0, 
            'distancia': 1.0
        }
    }
    return render(request, 'simulacoes/lei_gravitacao_universal_newton.html', context)

####################### Demais funções auxiliares #######################
def gerar_grafico_plotly(x, y, velocidade, angulo, gravidade):
    
    # Criação da figura com o ponto inicial e linha começando do ponto 0
    fig = go.Figure(
        data=[
            go.Scatter(
                x=[x[0]], y=[y[0]],
                mode='lines+markers',
                line=dict(color='red'),
                marker=dict(size=10),
                name='Trajetória'
            )
        ],
        layout=go.Layout(
            title='Trajetória do Projétil',
            xaxis_title='Distância (m)',
            yaxis_title='Altura (m)',
            xaxis=dict(range=[0, max(x) * 1.1], showgrid=True),
            yaxis=dict(range=[0, max(y) * 1.2], showgrid=True),
            height=500,
            margin=dict(b=80),
            updatemenus=[{
                "type": "buttons",
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [None, {
                            "frame": {"duration": 50, "redraw": True},
                            "fromcurrent": True,
                            "transition": {"duration": 0}
                        }]
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [[None], {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }]
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 70},
                "showactive": False,
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }],
            sliders=[{
                "steps": [
                    {
                        "method": "animate",
                        "args": [[f"frame{k}"], {"mode": "immediate", "frame": {"duration": 0}, "transition": {"duration": 0}}],
                        "label": f"{k}"
                    } for k in range(len(x))
                ],
                "transition": {"duration": 0},
                "x": 0.1,
                "xanchor": "left",
                "y": -0.15,
                "yanchor": "top"
            }]
        ),
        frames=[
            go.Frame(
                data=[
                    go.Scatter(
                        x=x[:i+1],
                        y=y[:i+1],
                        mode='lines+markers',
                        line=dict(color='red'),
                        marker=dict(size=10)
                    )
                ],
                name=f"frame{i}"
            ) for i in range(len(x))
        ]
    )

    # Rodapé com parâmetros
    rodape = f"Velocidade = {velocidade} m/s, Ângulo = {angulo}º, Gravidade = {gravidade} m/s²"
    fig.add_annotation(
        text=rodape,
        xref="paper", yref="paper",
        x=0.5, y=-0.25,
        showarrow=False,
        font=dict(size=12, color='gray'),
        align='center'
    )

    return fig



